from mcp_server.broker import generate_model_prompt

url = "opc.tcp://localhost:4840"
prompt = generate_model_prompt(url)
print(prompt)
