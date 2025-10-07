/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { debounce } from "@web/core/utils/timing";

export class AutoSaveFormController extends FormController {
    setup() {
        super.setup();
        // Preparamos un autoguardado con debounce (espera 2 segundos después de escribir)
        this.debouncedSave = debounce(this._autoSave.bind(this), 2000);
    }

    async onRecordChanged(event) {
        await super.onRecordChanged(event);

        // Solo ejecuta autoguardado si es modelo 'vifac.beneficiaria'
        if (this.model.root && this.model.root.resModel === "vifac.beneficiaria") {
            this.debouncedSave();
        }
    }

    async _autoSave() {
        if (!this.model.root.resId) return; // Evita guardar si es nuevo sin ID

        try {
            await this.model.saveRecord(this.model.root, { stayInEdit: true });
            console.log("✅ Autoguardado de beneficiaria exitoso");
        } catch (error) {
            console.warn("⚠️ Error durante autoguardado:", error);
        }
    }
}

// Registramos una nueva vista llamada 'form_autosave'
registry.category("views").add("form_autosave", {
    ...registry.category("views").get("form"),
    Controller: AutoSaveFormController,
});
