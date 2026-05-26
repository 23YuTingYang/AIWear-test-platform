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

    var data = {"OkPercent": 90.03436426116839, "KoPercent": 9.965635738831615};
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
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.45532646048109965, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "01 login auth"], "isController": false}, {"data": [0.9017857142857143, 500, 1500, "05 text search"], "isController": false}, {"data": [0.7318840579710145, 500, 1500, "04 my images"], "isController": false}, {"data": [0.0, 500, 1500, "09 merge"], "isController": false}, {"data": [0.0, 500, 1500, "02 upload person image"], "isController": false}, {"data": [0.6309523809523809, 500, 1500, "07 records"], "isController": false}, {"data": [0.0, 500, 1500, "03 upload cloth image"], "isController": false}, {"data": [0.0, 500, 1500, "08 edit"], "isController": false}]}, function(index, item){
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
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 291, 29, 9.965635738831615, 4896.264604810995, 14, 40770, 996.0, 21887.4, 27081.399999999987, 34947.95999999992, 0.9127321429131524, 18.028931682900858, 8.86864292648272], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["01 login auth", 5, 0, 0.0, 119.4, 109, 152, 111.0, 152.0, 152.0, 152.0, 0.10420357209845153, 0.04670843710272388, 0.027068506033386827], "isController": false}, {"data": ["05 text search", 56, 0, 0.0, 292.10714285714283, 19, 2914, 29.5, 991.8000000000001, 1125.1999999999996, 2914.0, 0.2050853851027441, 0.043660755812888884, 0.08471788857271559], "isController": false}, {"data": ["04 my images", 69, 0, 0.0, 996.9565217391303, 37, 21379, 391.0, 1421.0, 4341.5, 21379.0, 0.25368859541081007, 15.384423818969287, 0.08993062513098052], "isController": false}, {"data": ["09 merge", 25, 10, 40.0, 18660.72, 18, 39812, 25937.0, 33622.8, 38005.99999999999, 39812.0, 0.09576526019421194, 0.040169037654900305, 0.0601338499071077], "isController": false}, {"data": ["02 upload person image", 61, 10, 16.39344262295082, 4624.983606557377, 914, 15420, 3678.0, 8324.400000000003, 11282.5, 15420.0, 0.2036986328816344, 0.06975073736400612, 4.155120787445486], "isController": false}, {"data": ["07 records", 42, 0, 0.0, 796.7380952380955, 14, 3869, 644.0, 2196.4000000000015, 3088.650000000001, 3869.0, 0.15833581518440468, 5.669123885758824, 0.05535568538673523], "isController": false}, {"data": ["03 upload cloth image", 5, 0, 0.0, 10763.8, 3775, 20144, 5091.0, 20144.0, 20144.0, 20144.0, 0.08900281248887465, 0.03210706927088896, 26.51259932157606], "isController": false}, {"data": ["08 edit", 28, 9, 32.142857142857146, 17969.428571428572, 20, 40770, 21807.0, 29796.40000000001, 37959.749999999985, 40770.0, 0.09611951775464807, 0.043074765751585975, 0.04987339793651993], "isController": false}]}, function(index, item){
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
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["Value in json path '$.code' expected to be '200', but found '500'", 9, 31.03448275862069, 3.0927835051546393], "isController": false}, {"data": ["Value in json path '$.code' expected to be '200', but found '400'", 20, 68.96551724137932, 6.8728522336769755], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 291, 29, "Value in json path '$.code' expected to be '200', but found '400'", 20, "Value in json path '$.code' expected to be '200', but found '500'", 9, "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": ["09 merge", 25, 10, "Value in json path '$.code' expected to be '200', but found '500'", 5, "Value in json path '$.code' expected to be '200', but found '400'", 5, "", "", "", "", "", ""], "isController": false}, {"data": ["02 upload person image", 61, 10, "Value in json path '$.code' expected to be '200', but found '400'", 10, "", "", "", "", "", "", "", ""], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": ["08 edit", 28, 9, "Value in json path '$.code' expected to be '200', but found '400'", 5, "Value in json path '$.code' expected to be '200', but found '500'", 4, "", "", "", "", "", ""], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
