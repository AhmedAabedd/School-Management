/* @odoo-module */

import { Child } from "../child/child";
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Example extends Component {

    static template = "school.Example";
    static components = { Child }

    

}

registry.category("actions").add("school.action_example", Example);