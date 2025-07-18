from unitree_sdk2py.core.channel import ChannelFactoryInitialize

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 dds_test.py <interface>")
        sys.exit(1)
        
    try:
        print(f"Testing DDS on {sys.argv[1]}")
        ChannelFactoryInitialize(0, sys.argv[1])
        print("DDS initialized successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
