/* @odoo-module */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks"

export class ListViewAction extends Component {

    static template = "school.ListView";

    setup() {
        this.state = useState(
            {
                'records': []
            }
        );
        this.orm = useService("orm");
        this.loadRecords();
    };

    async loadRecords() {
        const result = await this.orm.searchRead('school.student', [], []) // (model.name, [domain], [fields])
        console.log(result)
        this.state.records = result;
    };

}

registry.category("actions").add("school.action_list_view", ListViewAction);