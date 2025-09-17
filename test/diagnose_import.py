import sys, os

print("CWD:", os.getcwd())
print("\nPYTHONPATH entries:")
for p in sys.path:
    print(" -", p)
print("\nRoot dir listing:")
print("\n".join(sorted(os.listdir("."))))
print("\nAttempting import opcua_client...")
try:
    import opcua_client

    print("IMPORT OK ->", opcua_client)
    print("opcua_client.__file__ =", getattr(opcua_client, "__file__", None))
except Exception as e:
    print("IMPORT ERROR:", type(e).__name__, e)
    import traceback

    traceback.print_exc()
