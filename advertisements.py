import streamlit as st

def show_advertisement():

    ad_html = """
    <!DOCTYPE html>
    <html>

    <head>

        <style>

            html,
            body {
                margin: 0;
                padding: 0;
                background-color: transparent;
                overflow: hidden;
            }

            .ad-container {
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }

        </style>

    </head>

    <body>

        <div class="ad-container">

            <script type="text/javascript">

                atOptions = {
                    'key': '131d995d7da9099eed9bc1316ad6db41',
                    'format': 'iframe',
                    'height': 250,
                    'width': 300,
                    'params': {}
                };

            </script>

            <script
                type="text/javascript"
                src="https://www.highrevenueformat.com/131d995d7da9099eed9bc1316ad6db41/invoke.js">
            </script>

        </div>

    </body>

    </html>
    """

    components.html(
        ad_html,
        height=270,
        scrolling=False
    )
