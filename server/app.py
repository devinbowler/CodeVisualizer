import os
import json
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import traceback

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
                # Parse the incoming JSON data
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                print("Request data received:", data)

                # Get Manim code from the request
                manim_code = data.get("manimCode", "")
                if not manim_code:
                    print("No Manim code provided.")
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Manim code is required"}).encode())
                    return

                print("Manim code received:", manim_code)

                # Write Manim code to a file
                script_path = os.path.join(WORKING_DIR, "circle.py")
                with open(script_path, "w") as script_file:
                    script_file.write(manim_code)

                print("Manim script written to:", script_path)

                # Define the output GIF path
                gif_filename = "circle.gif"
                gif_path = os.path.join(MEDIA_DIR, gif_filename)

                # Run the Manim command to render the GIF
                command = [
                    "manim",
                    "-qh",  # High-quality rendering
                    "-t",  # Transparent background
                    "--format=gif",  # Output as GIF
                    script_path,
                    "CreateCircle"
                ]
                print("Running Manim command:", " ".join(command))

                result = subprocess.run(command, cwd=WORKING_DIR, capture_output=True, text=True)

                if result.returncode != 0:
                    print(f"Manim error: {result.stderr}")
                    raise Exception(result.stderr)

                print("Manim command executed successfully.")

                # Check for the output file
                timeout = 15  # Max wait time in seconds
                start_time = time.time()
                while not os.path.exists(gif_path) or os.path.getsize(gif_path) == 0:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Rendering timed out.")
                    time.sleep(1)

                print("GIF generated at:", gif_path)

                # Send success response with GIF URL
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"videoUrl": f"http://localhost:8000/videos/{gif_filename}"}).encode())

            except Exception as e:
                print("Error Traceback:", traceback.format_exc())
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())


    def do_GET(self):
        # Serve GIF files dynamically
        if self.path.startswith("/videos/"):
            video_name = self.path.split("/")[-1]
            video_path = os.path.join(MEDIA_DIR, video_name)

            if os.path.exists(video_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/gif")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(video_path, "rb") as video_file:
                    self.wfile.write(video_file.read())
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GIF not found"}).encode())


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
