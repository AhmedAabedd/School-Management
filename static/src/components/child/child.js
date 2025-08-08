/* @odoo-module */

import { Component } from "@odoo/owl";

export class Child extends Component {

    static template = "school.Child";
    static props = {
        title: {type: String},
        list: {type: Array},
    };

}