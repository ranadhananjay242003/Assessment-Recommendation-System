# debug_recommender.py
print("Attempting to import Recommender...")
try:
    from backend.recommender import Recommender
    print("Import successful.")

    print("\nAttempting to initialize Recommender...")
    # This is the line that is likely failing
    rec = Recommender()
    print("Recommender initialized successfully!")

    # Optional: Test the recommend method directly
    # print("\nAttempting to get a recommendation...")
    # recommendations = rec.recommend("I need Java developers")
    # print("Recommendation successful:")
    # print(recommendations)

except Exception as e:
    print(f"\n--- AN ERROR OCCURRED ---")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    # This will give you the full traceback to see exactly where it failed
    import traceback
    traceback.print_exc()