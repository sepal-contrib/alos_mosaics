# It is strongly suggested to use a separate file to define the tiles of your process and then call them in your notebooks.
# it will help you to have control over their fonctionalities using object oriented programming

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from component import scripts
from component.message import ms
from component import parameter as pm

# the tiles should all be heriting from the sepal_ui Tile object
# if you want to create extra reusable object, you can define them in an extra widget.py file
class ExportTile(sw.Tile):
    def __init__(self, aoi_model, model, **kwargs):

        # gather the model
        self.aoi_model = aoi_model
        self.model = model

        # create an output alert
        self.output = sw.Alert()

        #
        self.backscatter = v.Switch(
            class_="ml-5", label=ms.export.backscatter, v_model=True
        )

        self.rfdi = v.Switch(class_="ml-5", label=ms.export.rfdi, v_model=True)

        self.texture = v.Switch(class_="ml-5", label=ms.export.texture, v_model=False)

        self.aux = v.Switch(class_="ml-5", label=ms.export.aux, v_model=False)

        self.fnf = v.Switch(class_="ml-5", label=ms.export.fnf, v_model=False)

        self.scale = v.TextField(label=ms.export.scale, v_model=25)

        # create buttons
        self.asset_btn = sw.Btn(
            ms.export.asset_btn, "mdi-download", disabled=True, class_="ma-5"
        )
        self.sepal_btn = sw.Btn(
            ms.export.sepal_btn, "mdi-download", disabled=True, class_="ma-5"
        )

        # bindings
        self.model.bind(self.backscatter, "backscatter").bind(self.rfdi, "rfdi").bind(
            self.texture, "texture"
        ).bind(self.aux, "aux").bind(self.fnf, "fnf").bind(self.scale, "scale")

        # note that btn and output are not a madatory attributes
        super().__init__(
            id_="export_widget",
            title=ms.export.title,
            inputs=[
                self.backscatter,
                self.rfdi,
                self.texture,
                self.aux,
                self.fnf,
                self.scale,
            ],
            alert=sw.Alert(),
            btn=v.Layout(row=True, children=[self.asset_btn, self.sepal_btn]),
        )

        # decorate each function as we are using multiple btns
        self._on_asset_click = su.loading_button(
            self.alert, self.asset_btn, debug=False
        )(self._on_asset_click)
        self._on_sepal_click = su.loading_button(
            self.alert, self.sepal_btn, debug=False
        )(self._on_sepal_click)

        # link the btn
        self.asset_btn.on_event("click", self._on_asset_click)
        self.sepal_btn.on_event("click", self._on_sepal_click)

    def _select_layers(self):

        dataset = None
        if self.model.backscatter:
            dataset = self.model.dataset.select(["HH", "HV", "HHHV_ratio"])
        if self.model.rfdi:
            if dataset:
                dataset = dataset.addBands(self.model.dataset.select(["RFDI"]))
            else:
                dataset = self.model.dataset.select(["RFDI"])
        if self.model.texture:
            if dataset:
                dataset = dataset.addBands(
                    self.model.dataset.select(
                        ["HH_var", "HH_idm", "HH_diss", "HV_var", "HV_idm", "HV_diss"]
                    )
                )
            else:
                dataset = self.model.dataset.select(
                    ["HH_var", "HH_idm", "HH_diss", "HV_var", "HV_idm", "HV_diss"]
                )
        if self.model.aux:
            if dataset:
                dataset = dataset.addBands(
                    self.model.dataset.select(["angle", "date", "qa"])
                )
            else:
                dataset = self.model.dataset.select(["angle", "date", "qa"])

        fnf_dataset = None
        if self.model.fnf and int(str(self.model.year)) <= 2017:
            fnf_dataset = self.model.dataset.select(f"fnf_{self.model.year}")

        return dataset, fnf_dataset

    def _on_asset_click(self, widget, data, event):

        dataset, fnf_dataset = self._select_layers()

        # export the results
        if dataset:
            asset_id = scripts.export_to_asset(
                self.aoi_model,
                dataset,
                pm.asset_name(self.aoi_model, self.model),
                self.model.scale,
                self.alert,
            )

        if fnf_dataset:
            asset_id = scripts.export_to_asset(
                self.aoi_model,
                fnf_dataset,
                pm.asset_name(self.aoi_model, self.model, True),
                self.model.scale,
                self.alert,
            )

        return

    def _on_sepal_click(self, widget, data, event):

        # get selected layers
        dataset, fnf_dataset = self._select_layers()

        if dataset:
            # export the results
            pathname = scripts.export_to_sepal(
                self.aoi_model,
                dataset,
                pm.asset_name(self.aoi_model, self.model),
                self.model.scale,
                self.alert,
            )

        if fnf_dataset:
            # export the results
            pathname = scripts.export_to_sepal(
                self.aoi_model,
                fnf_dataset,
                pm.asset_name(self.aoi_model, self.model, True),
                self.model.scale,
                self.alert,
            )

        return
