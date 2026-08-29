import streamlit.components.v1 as components

def show_advertisement():
    ad_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html,body{margin:0;padding:0;background:transparent;overflow:hidden}
            .ad-container{width:100%;display:flex;justify-content:center;align-items:center}
        </style>
    </head>
    <body>
        <div class="ad-container">
            <script type="text/javascript">
                atOptions={
                    'key':'131d995d7da9099eed9bc1316ad6db41',
                    'format':'iframe',
                    'height':250,
                    'width':300,
                    'params':{}
                };
            </script>
            <script type="text/javascript" src="https://www.highrevenueformat.com/131d995d7da9099eed9bc1316ad6db41/invoke.js"></script>
        </div>
    </body>
    </html>
    """

    components.html(ad_html, height=270, scrolling=False)

def show_advertisement1():
    ad_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html,body{margin:0;padding:0;background:transparent;overflow:hidden}
            .ad-container{width:100%;display:flex;justify-content:center;align-items:center}
        </style>
    </head>
    <body>
        <div class="ad-container">
            <script type="text/javascript">
                atOptions={
                    'key':'cfb3c02f1261778a6ed5018c09373968',
                    'format':'iframe',
                    'height':600,
                    'width':160,
                    'params':{}
                };
            </script>
            <script type="text/javascript" src="https://www.highrevenueformat.com/cfb3c02f1261778a6ed5018c09373968/invoke.js"></script>
        </div>
    </body>
    </html>
    """

    components.html(ad_html, height=620, scrolling=False)

def show_advertisement2():
    ad_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html,body{margin:0;padding:0;background:transparent;overflow:hidden}
            .ad-container{width:100%;display:flex;justify-content:center;align-items:center}
        </style>
    </head>
    <body>
        <div class="ad-container">
            <script type="text/javascript" src="https://pl31019682.profitableratecpmnetwork.com/a5/ce/c1/a5cec18624bd720b75fc810fe28973e8.js"></script>
        </div>
    </body>
    </html>
    """

    components.html(ad_html, height=270, scrolling=False)
