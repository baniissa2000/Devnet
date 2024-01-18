import paramiko
import time
import re
import tkinter as tk

#new commit
# standard connection test : pmnl1069 || APH connection test : VRF PNBO676 APH pnbo444
def send_command(channel, command):
    channel.send(command + '\n')
    time.sleep(3)  # Adjust the delay as needed

def get_router_info():
    router_name = input("Enter the router name (virtual router if APH connection): ")
    
    is_aph_router = input("Is it an APH type router? (yes/no): ").lower() == 'yes'

    if is_aph_router:
        aph_router_name = input("Enter the APH router name: ")
        return router_name, "APH", aph_router_name
    else:
        return router_name, "Standard", None

def find_words_with_pattern(input_string, pattern):
    """
    Find words in the input string that match the specified pattern.

    Args:
    - input_string (str): The input string to search.
    - pattern (str): The regular expression pattern.

    Returns:
    - List of matched words.
    """
    matches = re.findall(pattern, input_string)
    return matches


def submit():
    global router_name_var, router_type_var, aph_router_name_var
    
    router_name_var = router_name_entry.get()
    is_aph_router = aph_var.get()

    if is_aph_router:
        router_type_var = "APH"
        aph_router_name_var = aph_router_name_entry.get()
    else:
        router_type_var = "Standard"
        aph_router_name_var = None

    # Close the Tkinter window
    window.destroy()

# Call the function to get user input and receive the result
# Create the main window
window = tk.Tk()
window.title("Router Information")

# Create and place widgets in the window
tk.Label(window, text="Enter the router name:").pack(pady=5)
router_name_entry = tk.Entry(window)
router_name_entry.pack(pady=5)

tk.Label(window, text="Is it an APH type router?").pack(pady=5)
aph_var = tk.BooleanVar()
aph_checkbox = tk.Checkbutton(window, text="Yes", variable=aph_var)
aph_checkbox.pack(pady=5)

aph_router_name_entry = tk.Entry(window)
aph_router_name_entry.pack(pady=5)
aph_router_name_entry.insert(0, "APH Router Name")

submit_button = tk.Button(window, text="Submit", command=submit)
submit_button.pack(pady=10)

# Start the GUI event loop
window.mainloop()

# Access the stored information after the GUI is closed
if router_type_var == "APH":
    routername = aph_router_name_var
    virtualroutername = router_name_var
else :
    routername = router_name_var
try:

    # Main SSH session
    client = paramiko.SSHClient()
    client.load_host_keys(r"C:\Users\Hasan.Bani_Issa\.ssh\known_hosts")
    client.connect('57.255.78.22', username="s_oobeid", password="Imc@n2023")
    # Connectivity test to the router
    stdin, stdout, stderr = client.exec_command(f'ping {routername}')
    # Wait for the shell to be ready
    while not stdout.channel.recv_ready():
        time.sleep(1)
    output = stdout.read().decode('utf-8')
    print(output)
    # Checking if alive or unreachable
    search_word = "alive"

    if output.find(search_word) == -1:
        raise SystemExit("Exiting the program with an exception.")
    # Nested SSH session
    nested_ssh_command = f'ssh -o StrictHostKeyChecking=no s_oobeid@{routername} --yes'
    stdin, stdout, stderr = client.exec_command(nested_ssh_command, get_pty=True)

    # Wait for the shell to be ready
    while not stdout.channel.recv_ready():
        time.sleep(2)

    # Create a Channel for the nested SSH session
    nested_channel = stdout.channel

    # Send the password explicitly to handle the password prompt
    send_command(nested_channel, "Imc@n2023")

    # Wait for the shell to be ready
    while not nested_channel.recv_ready():
        time.sleep(1)

    # Read and print the output get rid off banner message
    output = nested_channel.recv(65536).decode('utf-8')

    # Send additional command to the nested session
    send_command(nested_channel, "show version | include uptime")

    # Wait for the shell to be ready
    while not nested_channel.recv_ready():
        time.sleep(1)

    # Read and print the output
    output = nested_channel.recv(65536).decode('utf-8')
    print("+++++++++++++++Logs+++++++++++++++++++")
    print(output)

    # Send additional command to the nested session
    send_command(nested_channel, "show ip bgp summary | B N")

    # Wait for the shell to be ready
    while not nested_channel.recv_ready():
        time.sleep(1)

    # Read and print the output
    output = nested_channel.recv(65536).decode('utf-8')
    print("+++++++++++++++Logs+++++++++++++++++++")
    print(output)

    if router_type_var == "APH":
        # Send additional command to the nested session
        send_command(nested_channel, f"show interfaces description | include {virtualroutername}")

        # Wait for the shell to be ready
        while not nested_channel.recv_ready():
            time.sleep(1)

        # Define a regular expression pattern to match any word ending with "net"
        mypattern = r"\b\w+net\b"

        # Read and print the output
        output = nested_channel.recv(65536).decode('utf-8')

        vrf_name = find_words_with_pattern(output, mypattern)

        # Send additional command to the nested session
        send_command(nested_channel, f"show ip bgp vpnv4 vrf {vrf_name[0]} summary")

        # Wait for the shell to be ready
        while not nested_channel.recv_ready():
            time.sleep(1)

        output = nested_channel.recv(65536).decode('utf-8')

        print("+++++++++++++++Logs+++++++++++++++++++")
        print(output)


    client.close()
except :
    print('error occured')