# 🌿 Plant Disease Classification Using Deep Learning
This is a Streamlit-based web application that uses a trained PyTorch model to detect plant diseases from leaf images. The model predicts the disease class and suggests possible solutions.

# 📌 Features
Upload leaf images to identify diseases.

Predicts class using a trained .pth model.

Shows the confidence score of the prediction.

Provides a short description and solution for each disease.

Simple UI powered by Streamlit.

Works locally in a single folder — no complex structure required.

🛠️ Technologies Used
Python

PyTorch (for the model)

Streamlit (for the web UI)

Torchvision (for image transformations)

🚀 How to Run the App
Clone this repository:

bash
Copy
Edit
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Install the required libraries:

bash
Copy
Edit
pip install -r requirements.txt
Download the trained model file:

The model is larger than 25MB and cannot be uploaded to GitHub.

🔗 Download model.pth from here

Place it in the same folder as app.py.

Run the app:

bash
Copy
Edit
streamlit run app.py
🖼️ Example
After uploading a leaf image, the app will show:

Predicted disease name

Confidence (%)

Disease description

Recommended solution
