/* @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class ListViewAction extends Component {

    static template = "school.ListView";

}

registry.category("actions").add("school.action_list_view", ListViewAction);