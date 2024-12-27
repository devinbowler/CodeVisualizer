import os
import json
import subprocess
import time
import re
import traceback
import uuid
from openai import OpenAI
from http.server import BaseHTTPRequestHandler, HTTPServer

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")

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

                user_prompt = data.get("textInput", "")
                if not user_prompt:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "A prompt is required"}).encode())
                    return

                print("User prompt received:", user_prompt)

                # Step 1: Generate Manim code using GPT-4
                try:
                    system_prompt = """
                    You are an AI designed to generate only Manim Python code. 
                    Your response must:
                    1. Follow Manim documentation guidelines.
                    2. Address the user's prompt accurately and concisely.
                    3. Contain only Python code with no explanations, comments, or additional text.
                    4. Avoid deprecated methods such as passing Mobject methods directly to Scene.play. Use the `.animate` syntax instead.

                    For example, when prompted to "generate Manim code to show a linked list of 5 nodes, and we are searching for the value 10 which is in the 4th node," the response should be:

                    from manim import *

                    class LinkedListSearch(Scene):
                        def construct(self):
                            # Create linked list nodes as rectangles with labels
                            node_values = [3, 7, 2, 10, 5]
                            nodes = []
                            arrows = []

                            for i, value in enumerate(node_values):
                                node = Rectangle(width=1.5, height=1, color=WHITE).move_to(3 * LEFT + i * 2 * RIGHT)
                                label = Text(str(value)).move_to(node.get_center())
                                self.add(node, label)
                                nodes.append((node, label))

                                if i > 0:
                                    arrow = Arrow(start=nodes[i-1][0].get_right(), end=node.get_left(), buff=0.1, color=WHITE)
                                    self.add(arrow)
                                    arrows.append(arrow)

                            # Highlight search process
                            for i, (node, label) in enumerate(nodes):
                                self.play(node.animate.set_fill(RED, opacity=0.5), run_time=0.5)
                                if int(label.text) == 10:
                                    self.play(node.animate.set_fill(GREEN, opacity=0.5), run_time=0.5)
                                    self.wait(1)
                                    break
                                else:
                                    self.play(node.animate.set_fill(BLACK, opacity=0.5), run_time=0.5)

                            # End scene
                            self.wait(1)
                    """


                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.7,
                        top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                        max_tokens=1000,  # Adjust based on response length
                    )
                    manim_code = response.choices[0].message.content.strip()

                    # Remove Markdown code block markers if present
                    if manim_code.startswith("```python"):
                        manim_code = manim_code[len("```python"):].strip()
                    if manim_code.endswith("```"):
                        manim_code = manim_code[:-len("```")].strip()

                except Exception as e:
                    print(f"Error generating Manim code: {e}")
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to generate Manim code"}).encode())
                    return

                print("Generated Manim code:", manim_code)

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
                script_path = os.path.join(WORKING_DIR, "generated_scene.py")
                with open(script_path, "w") as script_file:
                    script_file.write(manim_code)

                # Generate a unique filename for the output GIF
                unique_id = uuid.uuid4().hex
                gif_filename = f"scene_{unique_id}.gif"
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
                timeout = 10
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
            relative_path = self.path[len("/videos/"):]
            file_path = os.path.join(WORKING_DIR, "media", "videos", relative_path)

            print(f"Attempting to serve file: {file_path}")

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

