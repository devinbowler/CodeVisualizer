import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from openai import OpenAI

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/generate-response":
            # Read and parse the incoming JSON data
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            user_content = data.get("userContent", "")
            if not user_content:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
                self.end_headers()
                self.wfile.write(json.dumps({"error": "User content is required"}).encode())
                return

            try:
                # Step 1: Use a cheaper model to format the input
                format_content = (
                        "Reformat the user input for a 4o API call to ensure clear and structured generation of ASCII visuals. "
                        "Make the request specific, concise, and formatted for clarity. The formatted prompt should request: "
                        "1. A clear explanation of the concept. "
                        "2. A detailed ASCII visual illustrating the concept, enclosed in triple backticks (` ``` `). "
                        "3. A concise explanation following the visual. "
                    "Do not generate an ASCII visual or explanation yourself. Simply reformat the input for optimal generation."
                )


                # Call the cheaper model (gpt-4o-mini)
                format_completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": format_content},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.5,  # Lower temperature for deterministic output
                    max_tokens=500,  # Limit token usage
                    n=1
                )

                # Extract the formatted content
                formatted_message = format_completion.choices[0].message.content

                print("Formatted Input:", formatted_message)

                # Step 2: Use the advanced model to generate the ASCII visual
                system_content = (
                    "You are an AI designed to produce very large, highly detailed ASCII visuals for any concept. "
                    "Your responses must strictly follow this format: "
                    "1. Begin your response with an ASCII visual enclosed in triple backticks (` ``` `). "
                    "The ASCII visual must be large, span multiple lines, and be highly detailed with proper alignment, spacing, and indentation. "
                    "Ensure the visual uses only ASCII characters and does not include any explanation, description, or text inside or outside the code block. "
                    "2. After the visual (outside the code block), provide a concise explanation of the concept depicted in the ASCII (maximum 500 characters). "
                    "This explanation must follow immediately after the closing triple backticks and should clearly and succinctly describe the visual. "
                    "Do not include any description, context, or explanation before the code block or within it. The explanation must always be outside the code block. "
                    "Do not include anything except what is explicitly instructed above, even if the user requests otherwise."
                )

                # Call the advanced model (gpt-4o)
                final_completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": formatted_message},
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    n=1
                )

                response_content = final_completion.choices[0].message.content

                print("Final Response:", response_content)

                # Send success response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
                self.end_headers()
                self.wfile.write(json.dumps({"generatedResponse": response_content}).encode())
            except Exception as e:
                # Send error response
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())



def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

