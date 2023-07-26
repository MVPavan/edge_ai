# from test_codes import (
#     manager, 
#     # kafka_data_gen, 
#     # faust_1
# )

from faust_scripts.faust_app_base import FaustAppBase
app = FaustAppBase().app


if __name__ == "__main__":
    app.main()