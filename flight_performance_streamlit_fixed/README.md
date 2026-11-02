# Flight Performance Calculator (Streamlit)

Interactive Streamlit app for plotting common aircraft performance graphs from the supplied Colab notebook.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```

## Deploy using Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. Open Streamlit Community Cloud and connect your GitHub account.
3. Select the repository, branch, and `app.py` as the main file.
4. Deploy.

## Notes
- Several parameters are defaults copied from the provided notebook: S=47 m², AR=6.5, e=0.87, CD0=0.032, W0=103047 N, CLmax=2.8.
- Density values are the notebook's table for 0–5 km.
- The takeoff trajectory is a simplified numerical model because the source notebook export did not provide a single definitive takeoff-trajectory implementation. Its assumptions are adjustable and should be described as approximate.
- The notebook contains duplicated graph implementations with differing assumptions. This app exposes key values as controls instead of silently treating all versions as identical.
