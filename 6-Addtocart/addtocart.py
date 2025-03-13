import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from duckduckgo_search import DDGS

# Define the agent's state
class ShoppingState(TypedDict):
    driver: webdriver.Chrome
    product_url: str
    in_cart: bool
    payment_done: bool
    shipping_status: str
    tracking_url: str

# Initialize Selenium WebDriver
def setup_driver():
    service = Service(executable_path="C:/agenticAI/AgenticAIWorkspace/8-ExtractPDF Furquan/chromedriver.exe")  # Update path if needed
    driver = webdriver.Chrome(service=service)
    return driver

# Node 1: Search for Gillette razor (target product page)
def search_razor(state: ShoppingState) -> ShoppingState:
    print("Searching for Gillette razor...")
    with DDGS() as ddgs:
        query = "razor site:amazon.com Gillette inurl:/dp/"  # Target product pages
        results = ddgs.text(query, max_results=10)
        for result in results:
            url = result["href"]
            if "Gillette" in result["title"] and "amazon.com" in url and "/dp/" in url:
                print(f"Selected product URL: {url}")
                return {"product_url": url, "in_cart": False}
    print("No Gillette razor product page found.")
    return {"product_url": None, "in_cart": False}

# Node 2: Add to cart
def add_to_cart(state: ShoppingState) -> ShoppingState:
    if not state["product_url"]:
        print("No product URL available.")
        return state
    print("Adding Gillette razor to cart...")
    driver = state["driver"]
    driver.get(state["product_url"])
    try:
        # Wait for "Add to Cart" button
        add_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
        )
        add_button.click()
        time.sleep(2)  # Wait for cart to update
        print("Successfully added to cart.")
        return {"in_cart": True}
    except Exception as e:
        print(f"Error adding to cart: {e}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        return {"in_cart": False}

# Node 3: Wait for credit card input
def wait_for_payment(state: ShoppingState) -> ShoppingState:
    if not state["in_cart"]:
        print("Cart is empty, stopping.")
        return state
    driver = state["driver"]
    driver.get("https://www.amazon.com/gp/cart/view.html")
    print("Please log in, enter your credit card details, and complete checkout.")
    input("Press Enter after payment to resume tracking...")
    return {"payment_done": True}

# Node 4: Track shipping
def track_shipping(state: ShoppingState) -> ShoppingState:
    if not state["payment_done"]:
        print("Payment not completed, stopping.")
        return state
    driver = state["driver"]
    driver.get("https://www.amazon.com/gp/your-account/order-history")
    print("Tracking order status...")
    max_attempts = 10  # Limit retries
    attempt = 0
    while attempt < max_attempts:
        try:
            status = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "order"))
            )
            status_text = status.text.lower()
            if "shipped" in status_text:
                tracking_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Track')]")
                print("Order has shipped!")
                return {
                    "shipping_status": "shipped",
                    "tracking_url": tracking_link.get_attribute("href")
                }
            elif "delivered" in status_text:
                print("Order delivered!")
                return {"shipping_status": "delivered", "tracking_url": ""}
            else:
                print("Order not yet shipped. Checking again in 30 seconds...")
                time.sleep(30)
                driver.refresh()
        except Exception as e:
            print(f"Error tracking: {e}")
            time.sleep(30)
            driver.refresh()
        attempt += 1
    print("Tracking timed out after max attempts.")
    return {"shipping_status": "pending"}

# Build the agentic workflow
def build_workflow():
    workflow = StateGraph(ShoppingState)
    workflow.add_node("search", search_razor)
    workflow.add_node("cart", add_to_cart)
    workflow.add_node("payment", wait_for_payment)
    workflow.add_node("track", track_shipping)
    workflow.set_entry_point("search")
    workflow.add_edge("search", "cart")
    workflow.add_edge("cart", "payment")
    workflow.add_edge("payment", "track")
    workflow.add_edge("track", END)
    return workflow.compile()

# Run the agent
def run_shopping_agent():
    driver = setup_driver()
    initial_state = {
        "driver": driver,
        "product_url": None,
        "in_cart": False,
        "payment_done": False,
        "shipping_status": "pending",
        "tracking_url": ""
    }
    try:
        app = build_workflow()
        final_state = app.invoke(initial_state)
        print("\nFinal State:")
        print(f"Product URL: {final_state['product_url']}")
        print(f"In Cart: {final_state['in_cart']}")
        print(f"Payment Done: {final_state['payment_done']}")
        print(f"Shipping Status: {final_state['shipping_status']}")
        print(f"Tracking URL: {final_state['tracking_url']}")
    finally:
        driver.quit()
        print("Agent completed.")

if __name__ == "__main__":
    run_shopping_agent()