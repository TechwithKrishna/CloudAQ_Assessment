# Task 1: Resilient Web Form Automation Using C# and Selenium

## Project Overview

This project demonstrates resilient browser automation using **C#, .NET, and Selenium WebDriver**.

The objective is to automate form interactions on the CloudQA Automation Practice Form while reducing dependency on fixed element IDs, names, CSS classes, and HTML structure.

**Target URL:**  
https://app.cloudqa.io/home/AutomationPracticeForm

## Objectives

The automation performs the following operations:

1. Identifies the First Name input field and enters a name.
2. Identifies the Gender radio buttons and selects the requested option.
3. Identifies the State dropdown and selects the requested state.
4. Verifies that the expected values have been entered or selected.

## Technology Stack

- C#
- .NET SDK
- Selenium WebDriver
- Selenium Support
- Google Chrome

## Key Features

### 1. Dynamic Element Identification

Uses page labels, accessibility attributes, placeholders, IDs, names, titles, and nearby text to identify form elements.

### 2. First Name Automation

Finds the First Name field and enters the provided value.

### 3. Gender Selection

Identifies the appropriate radio button using its associated label and surrounding text.

### 4. State Dropdown Selection

Uses Selenium's `SelectElement` to select the requested state.

### 5. Verification

Checks whether the entered name, selected gender, and selected state match the expected values.

### 6. Configurable URL

The website URL and input values can be supplied at runtime.

## Project Setup

### Step 1: Create a .NET Console Project

```powershell
dotnet new console
```

### Step 2: Install Dependencies

```powershell
dotnet add package Selenium.WebDriver
dotnet add package Selenium.Support
```

### Step 3: Build the Project

```powershell
dotnet build
```

## Run the Project

Run with default configuration:

```powershell
dotnet run
```

Or provide custom inputs:

```powershell
dotnet run -- "https://app.cloudqa.io/home/AutomationPracticeForm" "Rahul" "Female" "Delhi"
```

## Expected Workflow

1. Launch Chrome browser.
2. Open the configured website.
3. Inspect the page to identify relevant form controls.
4. Enter the First Name.
5. Select Gender.
6. Select State.
7. Verify the selected values.
8. Report execution success or failure.

## Expected Result

The automation should successfully interact with the three required form controls and verify their values.

## Reliability Considerations

The locator strategy uses multiple attributes rather than relying on one fixed selector. It is heuristic, so significant changes to page markup, ambiguous labels, or custom controls may require updates.

## Conclusion

This project demonstrates how Selenium automation can be made more adaptable to changes in webpage structure through dynamic element identification and verification.
