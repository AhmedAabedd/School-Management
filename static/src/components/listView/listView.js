/* @odoo-module */

import { Component, useState, onWillUnmount } from "@odoo/owl";
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
        //this.rpc = useService("rpc");
        this.loadRecords();

        this.interval_id = setInterval(() => {this.loadRecords()}, 3000);
        onWillUnmount(() => {clearInterval(this.interval_id)});
    };

    async loadRecords() {
        const result = await this.orm.searchRead('school.student', [], []) // (model.name, [domain], [fields])
        console.log(result)
        this.state.records = result;
    };

    //async loadRecords() {
    //    await rpc("/web/dataset/call_kw/school.student/search_read", {
    //        model: 'school.student',
    //        method: 'search_read',
    //        args: [[]], //domain
    //        kwargs: { fields: ['id', 'reference', 'name', 'age', 'gender'] },
    //    });
    //    console.log(result)
    //}

}

registry.category("actions").add("school.action_list_view", ListViewAction);