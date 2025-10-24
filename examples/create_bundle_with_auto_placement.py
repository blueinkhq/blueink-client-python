#!/usr/bin/env python3
"""
Example: Create a Bundle with Auto Placement of Fields

This example demonstrates how to use the Auto Placement feature to automatically
place fields on your PDFs based on specific string inputs. The system will detect
strings like "Signature" or "Date" and automatically place the corresponding
fields next to them.

This is particularly useful for documents where the exact location of fields may vary,
but the strings indicating where they should be placed remain consistent.

Requirements:
    pip install python-dotenv colorama (optional)
"""

import os
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print(
        "Warning: python-dotenv not installed. Make sure BLUEINK_PRIVATE_API_KEY is set in environment."
    )

from blueink import Client, constants
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
        BLUE = CYAN = GREEN = YELLOW = RED = BLACK = ""

    class Style:
        RESET_ALL = BRIGHT = ""


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


def ask_field(field_name: str, default_value: str = None) -> str:
    """Ask user for input with optional default value"""
    if default_value:
        prompt = f"{field_name} (default: {default_value}): "
    else:
        prompt = f"{field_name}: "

    value = input(prompt).strip()

    if not value and default_value:
        return default_value

    while not value:
        print_yellow("⚠️  This field is required. Please enter a value.")
        value = input(prompt).strip()
        if not value and default_value:
            return default_value

    return value


def create_bundle_with_auto_placement():
    """
    Example: Create a Bundle with Auto Placement of Fields

    This demonstrates how to use auto-placement to automatically position
    signature and date fields based on text search in the PDF.
    """
    try:
        # Get requester email
        print_yellow("\n📧 Enter Requester Email:")
        requester_email = ask_field("Email")

        # Create a new bundle
        bundle_helper = BundleHelper(
            label="Bundle with Auto Placement Fields",
            email_subject="Please Sign This Document",
            email_message="This document uses auto-placement to automatically position signature fields.",
            is_test=False,  # Set to True for testing
        )
        print_blue("✓ Bundle data created using BundleHelper\n")

        # Get file URL
        print_yellow("📄 Enter a File URL:")
        print_gray("(The PDF should contain text like 'Signature', 'Date', etc.)")
        file_url = ask_field(
            "URL", default_value="https://www.irs.gov/pub/irs-pdf/fw4.pdf"
        )

        # Add document from URL
        doc_key = bundle_helper.add_document_by_url(file_url, key="DOC-1")
        print_blue("✓ Document added to bundle\n")

        # Add signer
        signer = bundle_helper.add_signer(
            name="John Doe",
            email=requester_email,
        )
        print_blue(f"✓ Signer added (key: {signer})\n")

        # Add auto-placement fields
        # This will search for text in the PDF and place fields there
        print_green("Adding auto-placement fields...")

        # Signature field - searches for "Signature" in the PDF
        bundle_helper.add_auto_placement(
            document_key=doc_key,
            kind=constants.FIELD_KIND.ESIGNATURE,  # 'sig' - signature field
            search="Signature",
            w=25,  # Width
            h=3,  # Height
            offset_x=0,
            offset_y=2,  # Offset 2 units below the search string
            editors=[signer],
        )
        print_green("✓ Auto-placement added: Signature field")

        # Date field - searches for "Date" in the PDF
        bundle_helper.add_auto_placement(
            document_key=doc_key,
            kind=constants.FIELD_KIND.DATE,  # 'dat' - date field
            search="Date",
            w=25,
            h=3,
            offset_x=0,
            offset_y=2,
            editors=[signer],
        )
        print_green("✓ Auto-placement added: Date field")

        # You can also add other types of auto-placements:
        # - Text/Input fields: constants.FIELD_KIND.INPUT ('inp')
        # - Checkboxes: constants.FIELD_KIND.CHECKBOX ('chk')
        # - Initials: constants.FIELD_KIND.INITIALS ('ini')
        # - Signing Date: constants.FIELD_KIND.SIGNINGDATE ('sdt')

        # Example: Add an input field for address
        bundle_helper.add_auto_placement(
            document_key=doc_key,
            kind=constants.FIELD_KIND.INPUT,
            search="Address",
            w=30,
            h=3,
            offset_x=0,
            offset_y=2,
            editors=[signer],
        )
        print_green("✓ Auto-placement added: Address input field\n")

        # Initialize the client
        try:
            client = Client()
        except ValueError as e:
            print_red(f"❌ Error initializing client: {e}")
            print("Please set BLUEINK_PRIVATE_API_KEY environment variable")
            return

        # Create the bundle
        print_yellow("Creating bundle with auto-placement fields...\n")
        response = client.bundles.create_from_bundle_helper(bundle_helper)

        if response.status == 201:
            bundle = response.data
            bundle_id = getattr(bundle, "id", "N/A")

            # Print success message with green background
            if HAS_COLOR:
                print(
                    f"\n{Fore.BLACK}{Style.BRIGHT}\033[42m✓ Bundle {bundle_id} was created successfully!{Style.RESET_ALL}\n"
                )
            else:
                print(f"\n✅ Bundle {bundle_id} was created successfully!\n")

            # Print bundle details
            print_cyan("Bundle Details:")
            print_gray("─" * 50)
            print(f"ID: {getattr(bundle, 'id', 'N/A')}")
            print(f"Label: {getattr(bundle, 'label', 'N/A')}")
            print(f"Status: {getattr(bundle, 'status', 'N/A')}")

            # Count documents and signers
            documents = getattr(bundle, "documents", [])
            packets = getattr(bundle, "packets", [])
            print(f"Documents: {len(documents) if documents else 0}")
            print(f"Signers: {len(packets) if packets else 0}")
            print_gray("─" * 50)

            # Print full response
            print("\nFull response:")
            import json

            try:
                if hasattr(bundle, "toDict"):
                    bundle_dict = bundle.toDict()
                elif isinstance(bundle, dict):
                    bundle_dict = dict(bundle)
                else:
                    bundle_dict = bundle
                print(json.dumps(bundle_dict, indent=2, ensure_ascii=False))
            except:
                print(bundle)
        else:
            print_red(f"\n❌ Error: HTTP {response.status}")

            # Print detailed error information
            import json

            print_red("\n📋 Error Details:")

            if hasattr(response, "data"):
                try:
                    if hasattr(response.data, "toDict"):
                        error_dict = response.data.toDict()
                    elif isinstance(response.data, dict):
                        error_dict = dict(response.data)
                    else:
                        error_dict = response.data

                    print(json.dumps(error_dict, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(response.data)

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

        # Try to extract detailed error information
        if hasattr(error, "response"):
            import json

            response = error.response
            print_red(f"\n📊 HTTP Status: {getattr(response, 'status_code', 'N/A')}")

            try:
                if hasattr(response, "json") and callable(response.json):
                    error_data = response.json()
                    print_red("\n📋 Error Details (JSON):")
                    print(json.dumps(error_data, indent=2, ensure_ascii=False))
                elif hasattr(response, "text"):
                    print_red("\n📋 Error Details (Text):")
                    print(response.text)
            except Exception as parse_error:
                print_red(f"\n⚠️  Could not parse error response: {parse_error}")
                if hasattr(response, "text"):
                    print_red("\n📋 Raw Response Text:")
                    print(response.text)
        else:
            import traceback

            print_red("\n📋 Full Error Traceback:")
            traceback.print_exc()


if __name__ == "__main__":
    create_bundle_with_auto_placement()
