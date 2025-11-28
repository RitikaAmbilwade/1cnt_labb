import socket
import math
import json

# Dictionary to store available trigonometric calculations
TRIG_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "degrees": math.degrees,
    "radians": math.radians
}

def process_calculator_request(operation, value):
    """Process trigonometric calculations"""
    try:
        value = float(value)
        if operation in TRIG_FUNCTIONS:
            result = TRIG_FUNCTIONS[operation](value)
            return f"Result of {operation}({value}) = {result}"
        else:
            return f"Error: Unsupported operation '{operation}'"
    except ValueError:
        return f"Error: Invalid number '{value}'"
    except Exception as e:
        return f"Error: {str(e)}"

# No longer needed for UDP implementation

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

# Main server code
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

local_ip = get_local_ip()
port = 12345

server_socket.bind(("0.0.0.0", port))
print(f"[SERVER] UDP Server running on {local_ip}:{port}")
print(f"[SERVER] Available trigonometric functions: {', '.join(TRIG_FUNCTIONS.keys())}")
print("[SERVER] Waiting for client messages...")

try:
    while True:
        data, client_address = server_socket.recvfrom(1024)
        message = data.decode().strip()
        
        # Process the received message
        if message.lower() == "hello":
            # Respond to hello message
            response = "Hello from Server!"
            print(f"[CLIENT {client_address}] Said hello")
            server_socket.sendto(response.encode(), client_address)
                
        elif message.lower() == "bye":
            # Client is saying goodbye
            print(f"[CLIENT {client_address}] Said bye")
            server_socket.sendto("bye!".encode(), client_address)
        
        elif message.startswith("CALC:"):
            # Handle calculator operation
            calc_request = message[5:]
            try:
                operation, value = calc_request.split(":")
                result = process_calculator_request(operation, value)
                print(f"[CLIENT {client_address}] Requested {operation}({value})")
                server_socket.sendto(result.encode(), client_address)
            except ValueError:
                error_msg = "Error: Invalid calculator request format. Use CALC:operation:value"
                server_socket.sendto(error_msg.encode(), client_address)
        
        else:
            # Regular message
            print(f"[CLIENT {client_address}] {message}")
            response = f"Message received: {message}"
            server_socket.sendto(response.encode(), client_address)

except KeyboardInterrupt:
    print("\n[SERVER] Shutting down...")
finally:
    server_socket.close()
    print("[SERVER] Closed.")
