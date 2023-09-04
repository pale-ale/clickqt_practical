def BLOB_BUTTON_STYLE_ENABLED(btnsizehalfpx: int):
    return f"""
        QToolButton {{
            background-color: #0f0;
            border-radius: {btnsizehalfpx}px;
            border-style: outset;
            padding: 5px;
        }}
        QToolButton:hover {{
            background-color: #9f9;
        }}
    """


def BLOB_BUTTON_STYLE_DISABLED(btnsizehalfpx: int):
    return f"""
        QToolButton {{
            background-color: #f00;
            border-radius: {btnsizehalfpx}px;
            border-style: outset;
            padding: 5px;
        }}
        QToolButton:hover {{
            background-color: #f99;
        }}
    """
