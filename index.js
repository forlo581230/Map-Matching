var express = require('express');
var path = require('path');
var bodyParser = require('body-parser');
var cors = require('cors');
// var cookieParser = require('cookie-parser');
var RateLimit = require('express-rate-limit');
var exec = require("child_process").exec;

var app = express();
var fs = require('fs');
var moment = require('moment');

// app.use(logger('dev'));
// app.use(bodyParser.json());
app.use(bodyParser.json({ "limit": "50mb" }));
app.use(bodyParser.urlencoded({ extended: false }));

// const corsOptions = {
//     origin: [
//         '*'
//     ],
//     allowedHeaders: ["Content-Type", "Cookie"],
//     credentials: true,
//     methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
// };
// app.use(cors(corsOptions));
// app.use(cookieParser('123456789'));

// var apiLimiter = new RateLimit({
//     windowMs: 60 * 1000,
//     max: 100,
//     delayMs: 0,
//     handler: function(req, res) {
//         res.status(429).send('Too many requests, please try again later.');
//     }
// });

// app.use(apiLimiter);

app.post('/mapMatching', function(req, res) {
    // console.log(req.headers);
    let buffers = [];
    req.on('data', (trunk) => {
        console.info(trunk.length);
        buffers.push(trunk);
    }).on('end', async() => {

        const buffer = Buffer.concat(buffers);
        // console.log(buffer.toString());
        let gpxfile = path.join(__dirname , `${moment().format('HHmmss.SSS')}.gpx`);
        fs.writeFileSync(gpxfile, buffer);
        console.log("產生->", gpxfile);

        exec(`bash mm.sh ${gpxfile}`, function(error, stdout, stderr) {
            // exec(`java -jar ../matching-web/target/graphhopper-map-matching-web-1.0-SNAPSHOT.jar match ${gpxfile}`, function(error, stdout, stderr) {
            if (stdout.length > 1) {
                // let list = stdout.replace(/'/g, `"`);
                // console.log(new Date().toString(), stdout);
                fs.unlink(gpxfile, (err) => { if (err) console.error('mapMatching delete error:',err); })
            } else {
                // console.log("you don\’t offer args");
            }
            if (error) {
                console.error(new Date().toString(), 'stderr :', stderr);
                res.status(400).json({ "err_code": "40000" });
            }else{
                res.status(200).json(getGPX_location(gpxfile + '.res.gpx'));
            }

        });


    })
    // .on('close', () => {
    //     console.log('close');
    //     res.status(400).json({ "err_code": "40000" });
    // })
    .on('error', (err) => {
        console.error('mapMatching error:',err);
        res.status(400).json({ "err_code": "40000" });
    });
});


function getGPX_location(file) {
    try {
        let gpx = fs.readFileSync(file).toString();
        let sp = gpx.split('\n');

        let ret_location = [];
        for (let i = 3; i < sp.length - 4; i++) {
            word = sp[i].split('"');
            lat = parseFloat(word[1]);
            lon = parseFloat(word[3]);

            ret_location.push({
                lat: lat,
                lng: lon
            });
        }


        let total_dist = 0;
        for (let i = 0; i < ret_location.length - 2; i++) {
            let dist = haversine(ret_location[i].lat, ret_location[i].lng, ret_location[i + 1].lat, ret_location[i + 1].lng);
            total_dist += dist;
        }

        let obj = {
            "locations": ret_location,
            "total_dist": total_dist
        };

        fs.unlink(file, (err) => { if (err) console.error(err); });
        // console.log(ret_location);

        return (obj);

    } catch (err) {
        console.log('getGPX_location', err);
        return null;
    }
}

// console.log(haversine(25.063700, 121.657045, 25.060677, 121.646430));

function haversine(lat1, lon1, lat2, lon2) {
    // console.log(lat1, lon1, "=>", lat2, lon2);
    /**
     *     Calculate the great circle distance between two points on the earth (specified in decimal degrees)
     */

    //將十進制度轉換成弧度
    // lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    lon1 = lon1 * (Math.PI / 180)
    lat1 = lat1 * (Math.PI / 180)
    lon2 = lon2 * (Math.PI / 180)
    lat2 = lat2 * (Math.PI / 180)

    //haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2
    c = 2 * Math.asin(Math.sqrt(a))
    r = 6371 // 地球平均半徑，單位為公里
    return c * r * 1000 //  單位：公尺
}

//getGPX_location(__dirname + '/150005.592.gpx');


// catch 404 and forward to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});

// error handler
app.use(function(err, req, res, next) {
    // set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    // render the error page
    res.status(err.status || 500).send('<h1>404</h1>');
});

module.exports = app;