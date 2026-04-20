import pandas as pd


def generate_csv(dataset):
    df = pd.DataFrame([
        {
            "product_name": product.name,
            "product_id": product.id,
            "url": product.url,
            "image": product.image,
            "price": product.price,
            "scraped_at": product.date,
        }
        for product in dataset
    ])
    try:
        df.to_csv(f"products.csv", index=False)
        print("CSV saved successfully")
    except Exception as e:
        print("Error saving CSV:", e)
