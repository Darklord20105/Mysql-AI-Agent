import json

from services.llm_service import generate_response


def main():

    print("Testing connection to Ollama...\n")

    # Test 1: Normal text response

    response = generate_response(
        prompt="Explain what a database is in two sentences."
    )

    print("TEXT RESPONSE:")
    print(response)

    print("\n" + "=" * 50 + "\n")

    # Test 2: Structured JSON response

    response = generate_response(
        system_prompt="You are a data analysis assistant. Return valid JSON only.",
        prompt="""
        Calculate the following:

        Total users: 120
        Active users: 95
        Inactive users: 25

        Return these fields:
        - total_users
        - active_users
        - inactive_users
        - active_percentage
        - inactive_percentage
        """,
        output_format="json"
    )

    print("JSON RESPONSE:")
    print(response)

    # Verify that the response is valid JSON.

    parsed_response = json.loads(response)

    print("\nJSON validation successful!")

    print("Active percentage:", parsed_response["active_percentage"])


if __name__ == "__main__":
    main()