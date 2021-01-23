const O = 0 //不是api的标志
const I = 1 //是api的标志
const tag_types = ["info", "success"]


var parseData = (data) => {
    let text = data.text
    if (text.length === 0) return []
    let labels = data.label.api
    let text_tokens = text.split("")
    var ret = []
    for (let i in text_tokens) {
        //console.log(text_tokens[i])
        ret.push({
            "text" : text_tokens[i],
            "index" : i,
            "flag" : O
        })
    }
    for (let [apiName, ranges] of Object.entries(labels)) {
        for (let [start, end] of ranges) {
            for (let i = start; i <= end; i++) {
                console.log("i: " + i)
                ret[i]["flag"] = I
                
            }
        }
    }
    //console.log(ret)
    return ret
}

var generateDataBack = (tokens) => {
    let text = ""
    let cur_start = -1
    let cur_end = -1
    let cur_api_name = ""
    let labels = {}
    for (let i = 0; i < tokens.length; i++) {
        text += tokens[i].text
        if (tokens[i].flag === O) {
            continue
        }
        if (cur_api_name.length === 0) {
            cur_start = i
        }
        cur_api_name += tokens[i].text
        if (i < tokens.length - 1 && tokens[i + 1].flag === O) {
            
            cur_end = i
            if (cur_api_name in labels) {
                labels[cur_api_name].push([cur_start, cur_end])
            } else {
                labels[cur_api_name] = [[cur_start, cur_end]]
            }
            cur_api_name = ""
        }
    }
    if (cur_api_name.length > 0) {
        cur_end = tokens.length - 1
        if (cur_api_name in labels) {
            labels[cur_api_name].push([cur_start, cur_end])
        } else {
            labels[cur_api_name] = [[cur_start, cur_end]]
        }
    }
    return {
        "text" : text,
        "label" : {
            "api" : labels
        }
    }
}

var saveObject = (obj, filename) => {
    let content = new Blob([JSON.stringify(obj)])
    let urlObject = window.URL || window.webkitURL || window
    let url = urlObject.createObjectURL(content)
    let el = document.createElement('a')
    el.href = url
    el.download = filename
    el.click()
    urlObject.revokeObjectURL(url)
}


export {
    O, I, tag_types, parseData, generateDataBack, saveObject
}