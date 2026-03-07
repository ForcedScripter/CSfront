from vector_store import create_collection


if __name__ == "__main__":
    # Add any domains you want collections for in this list.
    domains = [
        "car_booking",
        # "ecommerce",
    ]

    for domain in domains:
        create_collection(domain)
        print(f"✅ Collection for domain '{domain}' created successfully.")

