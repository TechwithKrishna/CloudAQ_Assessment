// using OpenQA.Selenium;
// using OpenQA.Selenium.Chrome;

// class Program
// {
//     static void Main()
//     {
//         IWebDriver driver = new ChromeDriver();

//         driver.Navigate().GoToUrl(
//             "https://app.cloudqa.io/home/AutomationPracticeForm"
//         );

//         Console.WriteLine("Website opened successfully!");

//         Console.ReadLine();

//         driver.Quit();
//     }
// }



using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Support.UI;
using System;
using System.Linq;
using System.Text.RegularExpressions;

class Program
{
    static void Main(string[] args)
    {
        string url = GetArg(args, "--url",
            "https://app.cloudqa.io/home/AutomationPracticeForm");

        string firstName = GetArg(args, "--firstName", "John");
        string gender = GetArg(args, "--gender", "Female");
        string state = GetArg(args, "--state", "India");

        using IWebDriver driver = new ChromeDriver();

        try
        {
            driver.Manage().Window.Maximize();
            driver.Navigate().GoToUrl(url);

            WebDriverWait wait =
                new WebDriverWait(driver, TimeSpan.FromSeconds(20));

            wait.Until(d =>
                ((IJavaScriptExecutor)d).ExecuteScript(
                    "return document.readyState")?.ToString() == "complete");

            // 1. First Name
            IWebElement nameField =
                FindElement(driver, "First Name", "text");

            nameField.Clear();
            nameField.SendKeys(firstName);

            Console.WriteLine("First Name entered successfully.");

            // 2. Gender
            // Find the radio button using its value
            IWebElement genderRadio = wait.Until(d =>
            {
                var radios = d.FindElements(
                    By.CssSelector("input[type='radio']"));

                return radios.FirstOrDefault(r =>
                    string.Equals(
                        r.GetAttribute("value"),
                        gender,
                        StringComparison.OrdinalIgnoreCase));
            });

            if (genderRadio == null)
                throw new Exception("Gender radio button not found.");

            if (!genderRadio.Selected)
                genderRadio.Click();

            Console.WriteLine("Gender selected successfully.");
            

            // 3. State
            IWebElement stateField =
                FindElement(driver, "State", "select");

            SelectElement dropdown =
                new SelectElement(stateField);

            var option = dropdown.Options.FirstOrDefault(x =>
                Normalize(x.Text) == Normalize(state) ||
                Normalize(x.GetAttribute("value")) == Normalize(state));

            if (option == null)
                throw new Exception("State option not found: " + state);

            option.Click();

            Console.WriteLine("State selected successfully.");

            // 4. Verification
            if (nameField.GetAttribute("value") != firstName)
                throw new Exception("First Name verification failed.");

            if (!genderRadio.Selected)
                throw new Exception("Gender verification failed.");

            if (Normalize(dropdown.SelectedOption.Text) !=
                Normalize(option.Text))
                throw new Exception("State verification failed.");

            Console.WriteLine("--------------------------------");
            Console.WriteLine("ALL THREE TESTS PASSED");
            Console.WriteLine("--------------------------------");
        }
        catch (Exception ex)
        {
            Console.WriteLine("TEST FAILED: " + ex.Message);
        }
        finally
        {
            driver.Quit();
        }
    }

    // Read command-line arguments
    static string GetArg(string[] args, string key, string fallback)
    {
        int index = Array.IndexOf(args, key);

        return index >= 0 && index + 1 < args.Length
            ? args[index + 1]
            : fallback;
    }

    // Normalize text
    static string Normalize(string value)
    {
        return Regex.Replace(
            (value ?? "").ToLowerInvariant(),
            @"[^a-z0-9]", "");
    }

    // Dynamic element identification
    static IWebElement FindElement(
        IWebDriver driver, string target, string kind)
    {
        string script = @"
            const target = arguments[0];
            const kind = arguments[1];

            function norm(s) {
                return (s || '').toLowerCase()
                    .replace(/[^a-z0-9]/g, '');
            }

            function visible(el) {
                return el && el.getClientRects().length > 0 &&
                    getComputedStyle(el).display !== 'none' &&
                    getComputedStyle(el).visibility !== 'hidden';
            }

            // RADIO BUTTON
            if (kind === 'radio') {
                let radios = [...document.querySelectorAll(
                    'input[type=radio]')];

                let matches = radios.filter(radio => {
                    let value = radio.value || '';
                    let aria = radio.getAttribute('aria-label') || '';

                    let labels = [...(radio.labels || [])]
                        .map(l => l.innerText || l.textContent)
                        .join(' ');

                    return norm(value) === norm(target) ||
                           norm(aria) === norm(target) ||
                           norm(labels) === norm(target);
                });

                matches = matches.filter(visible);

                return matches.length === 1 ? matches[0] : null;
            }

            // TEXTBOX
            if (kind === 'text') {
                let inputs = [...document.querySelectorAll(
                    'input[type=text], input:not([type]), textarea')];

                let matches = inputs.filter(el => {
                    let labels = [...(el.labels || [])]
                        .map(l => l.innerText || l.textContent)
                        .join(' ');

                    let placeholder =
                        el.getAttribute('placeholder') || '';

                    let aria = el.getAttribute('aria-label') || '';

                    return norm(labels).includes(norm(target)) ||
                           norm(placeholder) === norm(target) ||
                           norm(aria) === norm(target);
                }).filter(visible);

                return matches.length === 1 ? matches[0] : null;
            }

            // DROPDOWN
            if (kind === 'select') {
                let selects = [...document.querySelectorAll('select')];

                let matches = selects.filter(el => {
                    let labels = [...(el.labels || [])]
                        .map(l => l.innerText || l.textContent)
                        .join(' ');

                    let aria = el.getAttribute('aria-label') || '';

                    return norm(labels).includes(norm(target)) ||
                           norm(aria) === norm(target);
                }).filter(visible);

                return matches.length === 1 ? matches[0] : null;
            }

            return null;
        ";

        IWebElement element =
            ((IJavaScriptExecutor)driver)
            .ExecuteScript(script, target, kind) as IWebElement;

        if (element == null)
            throw new NoSuchElementException(
                "Unable to identify " + target + " uniquely.");

        return element;
    }
}

