/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 87.44769874476988, "KoPercent": 12.552301255230125};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.24686192468619247, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [0.0, 500, 1500, "03 上传服装图"], "isController": false}, {"data": [0.0, 500, 1500, "05 图搜图"], "isController": false}, {"data": [0.0, 500, 1500, "06 图片编辑"], "isController": false}, {"data": [0.7166666666666667, 500, 1500, "04 查询我的图片"], "isController": false}, {"data": [0.0, 500, 1500, "02 上传人物图"], "isController": false}, {"data": [0.25, 500, 1500, "08 查询历史记录"], "isController": false}, {"data": [0.9838709677419355, 500, 1500, "01 登录认证"], "isController": false}, {"data": [0.0, 500, 1500, "07 图片合并"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 239, 30, 12.552301255230125, 12337.464435146441, 21, 61458, 3422.0, 40772.0, 47576.0, 60170.6, 0.23262559348726206, 5.651025596601914, 42.93183859476378], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["03 上传服装图", 31, 3, 9.67741935483871, 38115.967741935485, 19807, 61458, 36405.0, 51829.6, 60636.6, 61458.0, 0.03035421409512619, 0.010808142701525055, 41.93755871184304], "isController": false}, {"data": ["05 图搜图", 30, 0, 0.0, 5822.5666666666675, 2161, 18198, 4878.5, 11880.900000000005, 16775.699999999997, 18198.0, 0.03074444601582724, 0.1498541544329392, 0.6114181605905393], "isController": false}, {"data": ["06 图片编辑", 30, 11, 36.666666666666664, 16728.63333333334, 21, 43203, 18427.0, 30058.300000000003, 38531.84999999999, 43203.0, 0.02994549919147152, 0.012993929173903495, 0.015123841795432313], "isController": false}, {"data": ["04 查询我的图片", 30, 0, 0.0, 695.2666666666668, 37, 3434, 118.0, 2246.7000000000016, 3322.35, 3434.0, 0.030930704910764915, 2.2421730415064287, 0.010964693244734048], "isController": false}, {"data": ["02 上传人物图", 31, 5, 16.129032258064516, 6540.096774193549, 1602, 60024, 4701.0, 9543.600000000002, 31369.799999999934, 60024.0, 0.03097104207565926, 0.010684346073920884, 0.6162519294459681], "isController": false}, {"data": ["08 查询历史记录", 28, 0, 0.0, 1898.3571428571431, 294, 4862, 1597.5, 3956.1000000000013, 4766.599999999999, 4862.0, 0.030961464034942224, 3.7866144796677172, 0.01082441809034113], "isController": false}, {"data": ["01 登录认证", 31, 0, 0.0, 163.5806451612903, 107, 1321, 112.0, 145.8, 741.9999999999986, 1321.0, 0.031075077386966913, 0.013929160664665834, 0.01256747238829011], "isController": false}, {"data": ["07 图片合并", 28, 11, 39.285714285714285, 28882.03571428571, 21, 60225, 37476.5, 48805.700000000004, 56170.49999999997, 60225.0, 0.02986281237301639, 0.012662948968719771, 0.018048712179548027], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["Value in json path '$.code' expected to be '200', but found '500'", 8, 26.666666666666668, 3.3472803347280333], "isController": false}, {"data": ["Value in json path '$.code' expected to be '200', but found '400'", 18, 60.0, 7.531380753138075], "isController": false}, {"data": ["504/Gateway Time-out", 4, 13.333333333333334, 1.6736401673640167], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 239, 30, "Value in json path '$.code' expected to be '200', but found '400'", 18, "Value in json path '$.code' expected to be '200', but found '500'", 8, "504/Gateway Time-out", 4, "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": ["03 上传服装图", 31, 3, "504/Gateway Time-out", 2, "Value in json path '$.code' expected to be '200', but found '400'", 1, "", "", "", "", "", ""], "isController": false}, {"data": [], "isController": false}, {"data": ["06 图片编辑", 30, 11, "Value in json path '$.code' expected to be '200', but found '500'", 6, "Value in json path '$.code' expected to be '200', but found '400'", 5, "", "", "", "", "", ""], "isController": false}, {"data": [], "isController": false}, {"data": ["02 上传人物图", 31, 5, "Value in json path '$.code' expected to be '200', but found '400'", 4, "504/Gateway Time-out", 1, "", "", "", "", "", ""], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": ["07 图片合并", 28, 11, "Value in json path '$.code' expected to be '200', but found '400'", 8, "Value in json path '$.code' expected to be '200', but found '500'", 2, "504/Gateway Time-out", 1, "", "", "", ""], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
