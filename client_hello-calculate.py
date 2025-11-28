import socket
import math

# Dictionary of available trigonometric operations
TRIG_FUNCTIONS = {
    "sin": "Sine (radians)",
    "cos": "Cosine (radians)",
    "tan": "Tangent (radians)",
    "asin": "Arc sine",
    "acos": "Arc cosine",
    "atan": "Arc tangent",
    "sinh": "Hyperbolic sine",
    "cosh": "Hyperbolic cosine",
    "tanh": "Hyperbolic tangent",
    "degrees": "Convert radians to degrees",
    "radians": "Convert degrees to radians"
}

def display_calculator_help():
    print("\n=== Calculator Functions ===")
    for func, description in TRIG_FUNCTIONS.items():
        print(f"  {func}: {description}")
    print("\nUsage: /calc <function> <value>")
    print("Example: /calc sin 1.57")
    print("===========================\n")

# Main client code
print("=== UDP Client with Chat & Trigonometric Calculator ===")
server_ip = input("Enter server IP address: ").strip()
if not server_ip:
    server_ip = "localhost"

port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (server_ip, port)

print(f"[CLIENT] UDP Client ready to communicate with {server_ip}:{port}")
print("[CLIENT] Commands:")
print("  - hello: Say hello to server")
print("  - /calc <function> <value>: Perform trigonometric calculation")
print("  - /help: Show available calculator functions")
print("  - bye: Exit client")
print("\n[CLIENT] You can start sending messages...")

try:
    # Send initial hello message
    client_socket.sendto("hello".encode(), server_address)
    
    # Wait for response with timeout
    client_socket.settimeout(5)
    try:
        data, _ = client_socket.recvfrom(1024)
        print(f"[SERVER] {data.decode()}")
    except socket.timeout:
        print("[CLIENT] No response from server. Server might be offline.")
    
    # Reset timeout
    client_socket.settimeout(None)
    
    # Main client loop
    while True:
        user_input = input("[CLIENT] You: ")
        
        if user_input.lower() == "bye":
            client_socket.sendto("bye".encode(), server_address)
            print("[CLIENT] You ended the communication.")
            
            # Wait for server's bye
            client_socket.settimeout(2)
            try:
                data, _ = client_socket.recvfrom(1024)
                print(f"[SERVER] {data.decode()}")
            except socket.timeout:
                pass
            break
            
        elif user_input.lower() == "/help":
            display_calculator_help()
            continue
            
        elif user_input.startswith("/calc "):
            # Parse calculator command
            parts = user_input[6:].strip().split()
            
            if len(parts) != 2:
                print("[CLIENT] Error: Invalid format. Use '/calc <function> <value>'")
                continue
                
            operation, value = parts
            
            if operation not in TRIG_FUNCTIONS:
                print(f"[CLIENT] Error: Unknown operation '{operation}'")
                print(f"[CLIENT] Available operations: {', '.join(TRIG_FUNCTIONS.keys())}")
                continue
                
            try:
                # Send calculation request to server
                calc_request = f"CALC:{operation}:{value}"
                client_socket.sendto(calc_request.encode(), server_address)
                
                # Wait for response
                data, _ = client_socket.recvfrom(1024)
                print(f"[SERVER] {data.decode()}")
                
            except Exception as e:
                print(f"[CLIENT] Error: {e}")
                
        else:
            # Send regular message
            client_socket.sendto(user_input.encode(), server_address)
            
            # Wait for response
            data, _ = client_socket.recvfrom(1024)
            print(f"[SERVER] {data.decode()}")
            
except KeyboardInterrupt:
    print("\n[CLIENT] Shutting down...")
except Exception as e:
    print(f"[CLIENT ERROR] {e}")
finally:
    client_socket.close()
    print("[CLIENT] Closed.")