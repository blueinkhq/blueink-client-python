#!/usr/bin/env python3
"""
Example: Create a Bundle from an Envelope Template (Interactive)

This example demonstrates how to create a bundle using an envelope template
with the Blueink Python SDK. It provides an interactive CLI experience similar
to the JavaScript version, allowing users to:
1. List available envelope templates
2. Select a template interactively
3. Create a bundle from the selected template

Requirements:
    pip install python-dotenv

Note: For colored output, you can optionally install:
    pip install colorama
"""

import os
import sys
from typing import List, Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print(
        "Warning: python-dotenv not installed. Make sure BLUEINK_PRIVATE_API_KEY is set in environment."
    )

from blueink import Client
from blueink.bundle_helper import BundleHelper

# Try to import colorama for colored output (optional)
try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Fallback: no colors
    class Fore:
        BLUE = CYAN = GREEN = YELLOW = RED = ""

    class Style:
        RESET_ALL = ""


def print_blue(text: str):
    """Print text in blue"""
    print(f"{Fore.BLUE}{text}{Style.RESET_ALL}")


def print_green(text: str):
    """Print text in green"""
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")


def print_yellow(text: str):
    """Print text in yellow"""
    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")


def print_red(text: str):
    """Print text in red"""
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")


def print_cyan(text: str):
    """Print text in cyan"""
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")


def print_gray(text: str):
    """Print text in gray (using dim style)"""
    if HAS_COLOR:
        print(f"{Style.DIM}{text}{Style.RESET_ALL}")
    else:
        print(text)


def ask_field(field_name: str) -> str:
    """Ask user for input until a non-empty value is provided"""
    value = ""
    while not value:
        value = input(f"{field_name}: ").strip()
        if not value:
            print_yellow("⚠️  This field is required. Please enter a value.")
    return value


def list_envelope_templates(client: Client) -> List:
    """List all available envelope templates"""
    print_blue("\n📋 Fetching available Envelope Templates...\n")

    try:
        response = client.envelope_templates.list()

        if not response.data or len(response.data) == 0:
            print_yellow("⚠️  No envelope templates found in your account.")
            return []

        print_green(f"✓ Found {len(response.data)} envelope template(s):\n")
        print_gray("─" * 80)

        for index, template in enumerate(response.data, 1):
            template_name = getattr(template, "name", "Unnamed Template")
            template_id = getattr(template, "id", "N/A")
            template_desc = getattr(template, "description", None)

            print_cyan(f"{index}. {template_name}")
            print_gray(f"   ID: {template_id}")
            if template_desc:
                print_gray(f"   Description: {template_desc}")
            print_gray("─" * 80)

        return response.data

    except Exception as error:
        print_red("✗ Error fetching envelope templates:")
        if hasattr(error, "response"):
            print(
                error.response.data
                if hasattr(error.response, "data")
                else error.response
            )
        else:
            print(str(error))
        return []


def ask_envelope_template_id(templates: List) -> str:
    """Ask user to select an envelope template"""
    if not templates:
        print_yellow("\nNo templates available. Please enter a template ID manually.")
        return ask_field("envelope_template_id")

    print("\nSelect an Envelope Template:")
    for index, template in enumerate(templates, 1):
        template_name = getattr(template, "name", "Unnamed Template")
        template_id = getattr(template, "id", "N/A")
        print(f"  {index}. {template_name} (ID: {template_id})")

    print(f"  {len(templates) + 1}. Enter a different template ID manually")

    while True:
        try:
            choice = input(f"\nEnter your choice (1-{len(templates) + 1}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(templates):
                selected_template = templates[choice_num - 1]
                return getattr(selected_template, "id")
            elif choice_num == len(templates) + 1:
                return ask_field("envelope_template_id")
            else:
                print_yellow(
                    f"⚠️  Please enter a number between 1 and {len(templates) + 1}"
                )
        except ValueError:
            print_yellow("⚠️  Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def create_bundle_from_envelope_template():
    """Main function to create a bundle from an envelope template"""
    try:
        # Get requester email
        requester_email = ask_field("requester_email")

        # Create BundleHelper with initial data
        bundle_helper = BundleHelper(
            label="New Bundle Created Using Envelope Template",
            email_subject="Yay First Bundle",
            email_message="This is your first bundle.",
        )
        print("Test Bundle Data is added using BundleHelper Class.\n")

        # Initialize the client
        try:
            client = Client()
        except ValueError as e:
            print_red(f"❌ Error initializing client: {e}")
            print("Please set BLUEINK_PRIVATE_API_KEY environment variable")
            return

        # List all available envelope templates
        templates = list_envelope_templates(client)

        # Ask user to select a template
        envelope_template_id = ask_envelope_template_id(templates)

        # Set the envelope template
        bundle_helper.set_envelope_template(template_id=envelope_template_id)
        print("Test Envelope Template is added using BundleHelper Class.\n")

        # Add a signer
        bundle_helper.add_signer(
            key="signer-11",
            name="The Signer One",
            email=requester_email,
        )
        print("Test Signer is added using BundleHelper Class.\n")

        print("Creating a new Bundle...")

        # Create the bundle
        response = client.bundles.create_from_envelope_template_helper(bundle_helper)

        if response.status == 201:
            bundle = response.data
            bundle_id = getattr(bundle, "id", "N/A")

            # Print success message with green background (simulating chalk.bgGreen.black)
            if HAS_COLOR:
                print(
                    f"\n{Fore.BLACK}{Style.BRIGHT}\033[42mBundle {bundle_id} was created successfully.{Style.RESET_ALL}\n"
                )
            else:
                print(f"\n✅ Bundle {bundle_id} was created successfully.\n")

            # Print bundle details
            print("Bundle Details:")
            print(f"  ID: {getattr(bundle, 'id', 'N/A')}")
            print(f"  Status: {getattr(bundle, 'status', 'N/A')}")
            print(f"  Label: {getattr(bundle, 'label', 'N/A')}")

            # Print full response data
            print("\nFull Response Data:")
            print(bundle)
        else:
            print_red(f"\n❌ Error: HTTP {response.status}")

            # Print detailed error information from response.data
            import json

            print_red("\n📋 Error Details:")

            # response.data is a Munch object (supports both dict and dot notation)
            if hasattr(response, "data"):
                # Try to convert to dict for pretty printing
                try:
                    if hasattr(response.data, "toDict"):
                        error_dict = response.data.toDict()
                    elif isinstance(response.data, dict):
                        error_dict = dict(response.data)
                    else:
                        error_dict = response.data

                    print(json.dumps(error_dict, indent=2, ensure_ascii=False))
                except Exception as e:
                    # Fallback: just print the data as-is
                    print(response.data)

            # Also print the original response for debugging
            if hasattr(response, "original_response"):
                print_red("\n🔍 Raw Response Text:")
                print(response.original_response.text)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as error:
        print_red("\n✗ Error creating bundle:")
        print_red(f"Error Type: {type(error).__name__}")
        print_red(f"Error Message: {str(error)}")

        # Try to extract detailed error information from requests.HTTPError
        if hasattr(error, "response"):
            import json

            response = error.response
            print_red(f"\n📊 HTTP Status: {getattr(response, 'status_code', 'N/A')}")

            # Try to get JSON error details
            try:
                if hasattr(response, "json") and callable(response.json):
                    error_data = response.json()
                    print_red("\n📋 Error Details (JSON):")
                    print(json.dumps(error_data, indent=2, ensure_ascii=False))
                elif hasattr(response, "text"):
                    print_red("\n📋 Error Details (Text):")
                    print(response.text)
                elif hasattr(response, "content"):
                    print_red("\n📋 Error Details (Content):")
                    content = response.content
                    if isinstance(content, bytes):
                        try:
                            content = content.decode("utf-8")
                        except:
                            pass
                    print(content)
            except Exception as parse_error:
                print_red(f"\n⚠️  Could not parse error response: {parse_error}")
                if hasattr(response, "text"):
                    print_red("\n📋 Raw Response Text:")
                    print(response.text)
        else:
            # No response attribute, just print the error
            import traceback

            print_red("\n📋 Full Error Traceback:")
            traceback.print_exc()


if __name__ == "__main__":
    create_bundle_from_envelope_template()
