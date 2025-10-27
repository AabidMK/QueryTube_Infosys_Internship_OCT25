from supadata import Supadata

def get_supadata_methods(api_key):
    """
    Get all available methods from the Supadata client
    """
    client = Supadata(api_key=api_key)
    
    # Get all methods and attributes
    all_attributes = dir(client)
    
    # Filter out private methods (those starting with _)
    public_methods = [method for method in all_attributes if not method.startswith('_')]
    
    print("Available public methods in Supadata client:")
    print("=" * 50)
    for method in sorted(public_methods):
        print(f"- {method}")
    
    return public_methods

# Usage
if __name__ == "__main__":
    API_KEY = ""
    methods = get_supadata_methods(API_KEY)