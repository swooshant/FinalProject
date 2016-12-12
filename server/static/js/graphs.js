queue()
    .defer(d3.json, "/data")
    .await(makeGraphs);

function makeGraphs(error, apsJson) {
	
	//Clean apsJson data
	var wifiAccessPoints = apsJson;
	var dateFormat = d3.time.format("%Y-%m-%d %H:%M:%S");
	wifiAccessPoints.forEach(function(d) {
		d["timestamp"] = dateFormat.parse(d["date_posted"]);
		d["total_donations"] = +d["total_donations"];
		d["longitude"] = +d["lon"];
		d["latitude"] = +d["lat"];
	});

	//Create a Crossfilter instance
	var ndx = crossfilter(wifiAccessPoints);

	//Define Dimensions
	var timeDim = ndx.dimension(function(d) { return d["timestamp"]; });
	var encryptionDim = ndx.dimension(function(d) { return d["encryption"]; });
	var channelDim = ndx.dimension(function(d) { return d["channel"]; });
	var addressDim = ndx.dimension(function(d) { return d["address"]; });
	var nameDim = ndx.dimension(function(d) { return d["name"]; });
	var allDim = ndx.dimension(function(d) {return d;});

	//Define Groups
	var numRecordsByTime = timeDim.group();
	var encryptionGroup = encryptionDim.group();
	var channelGroup = channelDim.group();
	var addressGroup = addressDim.group();
	var nameGroup = nameDim.group();
	var all = ndx.groupAll();

	//Define values (to be used in charts)
	var minDate = timeDim.bottom(1)[0]["timestamp"];
	var maxDate = timeDim.top(1)[0]["timestamp"];

	// Charts
	var numberRecordsND = dc.numberDisplay("#number-records-nd");
	var timeChart = dc.barChart("#time-chart");
	var encryptionChart = dc.rowChart("#encryption-row-chart");
	var channelChart = dc.rowChart("#channel-row-chart");
	var addressChart = dc.rowChart("#address-row-chart");
	var nameChart = dc.rowChart("#name-row-chart");

	// Pass necessary parameters
	numberProjectsND
		.formatNumber(d3.format("d"))
		.valueAccessor(function(d){return d; })
		.group(all);

	timeChart
		.width(650)
		.height(140)
		.margins({top: 10, right: 50, bottom: 20, left: 20})
		.dimension(timeDim)
		.group(numRecordsByTime)
		.transitionDuration(500)
		.x(d3.time.scale().domain([minDate, maxDate]))
		.elasticY(true)
		.yAxis().ticks(4);

	encryptionChart
		.width(300)
		.height(100)
	        .dimension(encryptionDim)
	        .group(encryptionGroup)
	        .ordering(function(d) { return -d.value })
	        .colors(['#6baed6'])
	        .elasticX(true)
	        .xAxis().ticks(4);

	 channelChart
		.width(300)
		.height(150)
		.dimension(channelDim)
        	.group(channelGroup)
        	.colors(['#6baed6'])
        	.elasticX(true)
        	.labelOffsetY(10)
        	.xAxis().ticks(4);

	addressChart
		.width(300)
		.height(310)
		.dimension(addressDim)
		.group(addressGroup)
		.ordering(function(d) { return -d.value })
		.colors(['#6baed6'])
		.elasticX(true)
		.xAxis().ticks(4);

	nameChart
		.width(200)
		.height(510)
		.dimension(nameDim)
		.group(nameGroup)
		.ordering(function(d) { return -d.value })
		.colors(['#6baed6'])
		.elasticX(true)
		.labelOffsetY(10)
		.xAxis().ticks(4);


    dc.renderAll();

};
