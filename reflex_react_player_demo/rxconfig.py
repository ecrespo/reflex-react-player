import reflex as rx

config = rx.Config(
    app_name="reflex_react_player_demo",
    # Reflex 0.9+ configures the Radix theme through a plugin (App(theme=...) is deprecated).
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="light", accent_color="violet")
        ),
    ],
    disable_plugins=[rx.plugins.SitemapPlugin],
)
