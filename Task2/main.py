
import os
import json
import time
from dotenv import load_dotenv
from google import genai
from playwright.sync_api import sync_playwright

# Load Gemini API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key is missing.")

client = genai.Client(
    api_key=api_key,
    http_options={"api_version": "v1beta"}
)
MODEL = "gemini-2.5-flash"


# 1. Inspect webpage elements
def inspect_page(page):

    return page.evaluate("""
    () => [...document.querySelectorAll(
        'input, button, a, select, textarea, h1, h2, h3'
    )]
    .filter(el => {
        const style = getComputedStyle(el);

        return el.getClientRects().length > 0 &&
               style.display !== 'none' &&
               style.visibility !== 'hidden' &&
               el.innerText.trim().length < 150;
    })
    .map(el => ({
        tag: el.tagName,
        type: el.type || '',
        text: (el.innerText || el.textContent || '').trim(),
        placeholder: el.placeholder || '',
        label: [...(el.labels || [])]
            .map(x => x.innerText).join(' '),
        aria: el.getAttribute('aria-label') || ''
    }))
    .slice(0, 80);
    """)


# 2. Ask Gemini to understand the test

# 2. Ask Gemini to understand the test
def get_ai_action(test_case, page, history):

    elements = inspect_page(page)

    prompt = f"""
You are an AI browser testing assistant.

Understand the plain-English test case and choose
the next browser action.

TEST CASE:
{test_case}

CURRENT URL:
{page.url}

PAGE ELEMENTS:
{json.dumps(elements)}

PREVIOUS ACTIONS:
{json.dumps(history)}

Return exactly one JSON object.

Allowed actions:

fill:
{{"action":"fill","locator_type":"label",
"locator":"Email","value":"example@test.com"}}

click:
{{"action":"click","locator_type":"role",
"role":"button","locator":"Login"}}

select_option:
{{"action":"select_option","locator_type":"label",
"locator":"Country","value":"India"}}

assert_text:
{{"action":"assert_text","locator":"Dashboard"}}

assert_visible:
{{"action":"assert_visible","locator_type":"role",
"role":"heading","locator":"Dashboard"}}

assert_url:
{{"action":"assert_url","value":"dashboard"}}

wait:
{{"action":"wait","seconds":2}}

done:
{{"action":"done"}}

Rules:
- Use only elements found on the page.
- Prefer labels, roles and placeholders.
- Never invent credentials.
- Do not bypass CAPTCHA or security checks.
- Verify the expected result before returning done.
- Return need_input if required information is missing.
- Return valid JSON only.
- For headings, use short heading text only.
- Never use entire webpage text as a locator.
- Prefer exact visible heading names.
- Do not select hidden navigation elements.
- Use the smallest matching visible element for assertions.
"""

    for attempt in range(3):

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            return json.loads(response.text)

        except Exception as error:

            if attempt == 2:
                raise

            print(
                f"Gemini API error. Retrying {attempt + 1}/3..."
            )

            time.sleep(5)



# 3. Find webpage elements
def get_locator(page, step):

    locator_type = step.get("locator_type", "text")
    name = step.get("locator", "")

    if locator_type == "role":
        return page.get_by_role(
            step["role"], name=name, exact=False
        )

    if locator_type == "label":
        return page.get_by_label(name, exact=False)

    if locator_type == "placeholder":
        return page.get_by_placeholder(name, exact=False)

    if locator_type == "text":
        return page.get_by_text(name, exact=False)

    raise ValueError("Unsupported locator type")


# 4. Execute browser actions
def execute_action(page, step):

    action = step["action"]

    if action == "fill":
        locator = get_locator(page, step)

        if locator.count() != 1:
            raise Exception("Input field is missing or ambiguous.")

        locator.fill(step["value"])

    elif action == "click":
        locator = get_locator(page, step)

        if locator.count() != 1:
            raise Exception("Click target is missing or ambiguous.")

        locator.click()

    elif action == "select_option":
        locator = get_locator(page, step)

        if locator.count() != 1:
            raise Exception("Dropdown is missing or ambiguous.")

        locator.select_option(label=step["value"])

    elif action == "assert_text":
        locator = page.get_by_text(
            step["locator"], exact=False
        )

        locator.first.wait_for(
            state="visible", timeout=10000
        )

        return True

    elif action == "assert_visible":

        locator = get_locator(page, step)

        locator = locator.filter(visible=True)

        locator.first.wait_for(
            state="visible",
            timeout=15000
        )

        return True

    elif action == "assert_url":
        expected = step["value"].lower()

        if expected not in page.url.lower():
            raise AssertionError(
                "Expected URL not found: " + expected
            )

        return True

    elif action == "wait":
        page.wait_for_timeout(
            int(step.get("seconds", 2)) * 1000
        )

    elif action == "need_input":
        raise Exception(
            step.get("reason", "More information required.")
        )

    elif action == "done":
        return "DONE"

    else:
        raise Exception("Unknown action: " + action)

    return False


# 5. Run the complete test
def run_test(url, test_case):

    history = []
    assertions = 0

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("\nOpening website:", url)

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            for i in range(15):

                step = get_ai_action(
                    test_case, page, history
                )

                print("AI Action:", step)

                result = execute_action(page, step)

                if result == "DONE":

                    if assertions == 0:
                        raise Exception(
                            "No successful verification performed."
                        )

                    print("\nTEST RESULT: PASS")
                    return True

                if result is True:
                    assertions += 1

                history.append(step)

            raise Exception("Maximum actions reached.")

        except Exception as error:

            print("\nTEST RESULT: FAIL")
            print("Reason:", error)

            page.screenshot(path="failure.png")

            return False

        finally:
            browser.close()


# 6. Get input from user
if __name__ == "__main__":

    website = input("Enter website URL: ")

    test_case = input(
        "Enter plain-English test case: "
    )

    run_test(website, test_case)
