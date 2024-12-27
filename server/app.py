import os
import json
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import traceback
import uuid
import re

# Paths for scripts and rendered files
WORKING_DIR = r"C:\Users\devin\OneDrive\Desktop\code\CodeVisualizer\server"
MEDIA_DIR = os.path.join(WORKING_DIR, "media", "videos", "circle", "1080p60")
os.makedirs(MEDIA_DIR, exist_ok=True)  # Ensure the output directory exists


class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        print("POST request received.")
        if self.path == "/api/generate-video":
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                print("Request data received:", data)

                manim_code = data.get("manimCode", "")
                if not manim_code:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Manim code is required"}).encode())
                    return

                print("Manim code received:", manim_code)

                # Extract the class name dynamically
                class_match = re.search(r"class\s+(\w+)\s*\(.*Scene\):", manim_code)
                if not class_match:
                    print("No valid class found in the Manim code.")
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "No valid Scene class found in the code"}).encode())
                    return

                class_name = class_match.group(1)
                print(f"Extracted class name: {class_name}")

                # Write Manim code to a file
                script_path = os.path.join(WORKING_DIR, "code.py")
                with open(script_path, "w") as script_file:
                    script_file.write(manim_code)

                # Generate a unique filename for the output GIF
                unique_id = uuid.uuid4().hex
                gif_filename = f"circle_{unique_id}.gif"
                gif_path = os.path.join(MEDIA_DIR, gif_filename)

                # Run the Manim command to render the GIF
                command = [
                    "manim",
                    "-qh",
                    "-t",
                    "--format=gif",
                    "--output_file", 
                    gif_path,
                    script_path,
                    class_name,
                ]
                print("Running Manim command:", " ".join(command))

                result = subprocess.run(command, cwd=WORKING_DIR, capture_output=True, text=True)

                print(f"Manim stdout: {result.stdout}")
                print(f"Manim stderr: {result.stderr}")

                if result.returncode != 0:
                    raise Exception(result.stderr)

                # Wait for the file to be fully rendered
                # TO-DO: Change this based on code length
                timeout = 5
                start_time = time.time()
                while not os.path.exists(gif_path) or os.path.getsize(gif_path) == 0:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Rendering timed out. File: {gif_path}")
                    time.sleep(1)

                print(f"GIF successfully rendered: {gif_path}")

                # Send the response back with the generated GIF URL
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "videoUrl": f"http://localhost:8000/videos/circle/1080p60/{gif_filename}"
                }).encode())

            except Exception as e:
                print("Error Traceback:", traceback.format_exc())
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())


    def do_GET(self):
        if self.path.startswith("/videos/"):
            # Remove the '/videos/' prefix to get the relative path
            relative_path = self.path[len("/videos/"):]

            # Construct the full file path relative to MEDIA_DIR
            file_path = os.path.join(WORKING_DIR, "media", "videos", relative_path)

            print(f"Attempting to serve file: {file_path}")
            print(f"Both paths: {MEDIA_DIR, relative_path}")

            if os.path.exists(file_path):
                try:
                    self.send_response(200)
                    self.send_header("Content-Type", "image/gif")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    with open(file_path, "rb") as file:
                        self.wfile.write(file.read())
                except Exception as e:
                    print(f"Error serving file: {str(e)}")
                    self.send_response(500)
                    self.end_headers()
            else:
                print(f"File not found: {file_path}")
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "File not found"}).encode())


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()





# Use this code for ASCII version.

'''
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
'''
