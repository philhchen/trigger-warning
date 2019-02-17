// URL: https://beta.observablehq.com/@dvddddddvd/treehacks-2019-trigger-warning-demo
// Title: Treehacks 2019: Trigger-Warning - Demo
// Author: dvddddddvd (@dvddddddvd)
// Version: 344
// Runtime version: 1

const m0 = {
  id: "a9e838c1dd43780b@344",
  variables: [
    {
      inputs: ["md"],
      value: (function(md){return(
md`# Treehacks 2019: Trigger-Warning - Demo`
)})
    },
    {
      inputs: ["html"],
      value: (function(html){return(
html`<span contenteditable=true class="tw-demo">-type stuff here-</span>`
)})
    },
    {
      name: "initial trigger",
      value: (function(){return(
0.5
)})
    },
    {
      name: "mutable trigger",
      inputs: ["Mutable","initial trigger"],
      value: (M, _) => new M(_)
    },
    {
      name: "trigger",
      inputs: ["mutable trigger"],
      value: _ => _.generator
    },
    {
      name: "viewof THRESHOLD",
      inputs: ["slider"],
      value: (function(slider){return(
slider({
  title: "Highlight threshold",
  value: 0.53
})
)})
    },
    {
      name: "THRESHOLD",
      inputs: ["Generators","viewof THRESHOLD"],
      value: (G, _) => G.input(_)
    },
    {
      inputs: ["md"],
      value: (function(md){return(
md`## Upload model/tokenizer`
)})
    },
    {
      name: "viewof e1",
      inputs: ["file"],
      value: (function(file){return(
file({
  title: "model.json",
  description: "Upload the model file.",
  accept: ".json",
  multiple: true,
})
)})
    },
    {
      name: "e1",
      inputs: ["Generators","viewof e1"],
      value: (G, _) => G.input(_)
    },
    {
      name: "viewof e2",
      inputs: ["file"],
      value: (function(file){return(
file({
  title: "weight shards",
  description: "Upload the weights file.",
  multiple: true,
})
)})
    },
    {
      name: "e2",
      inputs: ["Generators","viewof e2"],
      value: (G, _) => G.input(_)
    },
    {
      name: "viewof e3",
      inputs: ["file"],
      value: (function(file){return(
file({
  title: "tokenizer.json",
  description: "Upload the tokenizer file.",
  accept: ".json",
  multiple: true,
})
)})
    },
    {
      name: "e3",
      inputs: ["Generators","viewof e3"],
      value: (G, _) => G.input(_)
    },
    {
      name: "model_rawText",
      inputs: ["Files","e1"],
      value: (function(Files,e1){return(
Files.text(e1[0])
)})
    },
    {
      name: "tokenizer_rawText",
      inputs: ["Files","e3"],
      value: (function(Files,e3){return(
Files.text(e3[0])
)})
    },
    {
      name: "tokenizer",
      inputs: ["tokenizer_rawText"],
      value: (function(tokenizer_rawText){return(
JSON.parse(tokenizer_rawText)
)})
    },
    {
      name: "model",
      inputs: ["tf","e1","e2"],
      value: (async function(tf,e1,e2){return(
await tf.loadModel(tf.io.browserFiles([e1[0],...e2]))
)})
    },
    {
      inputs: ["md"],
      value: (function(md){return(
md`## Processing`
)})
    },
    {
      name: "predict",
      inputs: ["tf","tokenizer","model","mutable trigger","trigger"],
      value: (function(tf,tokenizer,model,$0,trigger){return(
(text) => {
  // taken from https://beta.observablehq.com/@jashkenas/sentiment-analysis-with-tensorflow-js
  const MAX_LEN = 20;
  let trimmed = text.trim().toLowerCase().replace(/(\.|\,|\!)/g, '').split(' ');
  let inputBuffer = tf.buffer([1, MAX_LEN], "float32");
  trimmed.forEach((word, i) => inputBuffer.set(tokenizer[word], 0, i))
  // trimmed.forEach((word, i) => inputBuffer.set(1, 0, i))
  const input = inputBuffer.toTensor();
  console.log(inputBuffer)
  const predictOut = model.predict(input);
  $0.value = predictOut.dataSync()[0];
  predictOut.dispose();
  return trigger;
}
)})
    },
    {
      inputs: ["md"],
      value: (function(md){return(
md`## Highlight behaviour`
)})
    },
    {
      inputs: ["enableHighlighting","d3","tfJudge"],
      value: (function(enableHighlighting,d3,tfJudge){return(
enableHighlighting(d3.select(".tw-demo"), tfJudge)
)})
    },
    {
      name: "enableHighlighting",
      inputs: ["unhilight","_","hilight"],
      value: (function(unhilight,_,hilight){return(
(d3Sel,judge) => {
  d3Sel
  .on("keydown", () => { unhilight(d3Sel); })
  .on("keyup", () =>{ _.debounce(hilight, 2000)(d3Sel,judge); })
  return "initialized!"
}
)})
    },
    {
      name: "hilight",
      value: (function(){return(
(d3Sel, judge) => {
  console.log("hi-called")
  let h = d3Sel;
  let text = h.property("innerHTML");
  if (judge(text)) {
    console.log("color change!")
    h.style("background-color", "#FFFF00")
  }
}
)})
    },
    {
      name: "unhilight",
      value: (function(){return(
(d3Sel) => {
  d3Sel.style("background-color","#FFFFFF")
}
)})
    },
    {
      inputs: ["md"],
      value: (function(md){return(
md`### Judge functions`
)})
    },
    {
      name: "naiveJudge",
      value: (function(){return(
(text) => {
  return text.match("fuck");
}
)})
    },
    {
      name: "tfJudge",
      inputs: ["predict","THRESHOLD"],
      value: (function(predict,THRESHOLD){return(
(text) => {
  return (predict(text) < THRESHOLD);
}
)})
    },
    {
      inputs: ["md"],
      value: (function(md){return(
md`## Imports`
)})
    },
    {
      from: "@jashkenas/inputs",
      name: "slider",
      remote: "slider"
    },
    {
      from: "@jashkenas/inputs",
      name: "file",
      remote: "file"
    },
    {
      from: "@jashkenas/inputs",
      name: "textarea",
      remote: "textarea"
    },
    {
      name: "tf",
      inputs: ["require"],
      value: (function(require){return(
require("@tensorflow/tfjs")
)})
    },
    {
      name: "d3",
      inputs: ["require"],
      value: (function(require){return(
require("d3")
)})
    }
  ]
};

const m1 = {
  id: "@jashkenas/inputs",
  variables: [
    {
      name: "slider",
      inputs: ["input"],
      value: (function(input){return(
function slider(config = {}) {
  let {value, min = 0, max = 1, step = "any", precision = 2, title, description, getValue, format, display, submit} = config;
  if (typeof config == "number") value = config;
  if (value == null) value = (max + min) / 2;
  precision = Math.pow(10, precision);
  if (!getValue) getValue = input => Math.round(input.valueAsNumber * precision) / precision;
  return input({
    type: "range", title, description, submit, format, display,
    attributes: {min, max, step, value},
    getValue
  });
}
)})
    },
    {
      name: "file",
      inputs: ["input"],
      value: (function(input){return(
function file(config = {}) {
  let {multiple, accept, title, description} = config;
  const form = input({
    type: "file", title, description,
    attributes: {multiple, accept},
    action: form => {
      form.input.onchange = () => {
        form.value = multiple ? form.input.files : form.input.files[0];
        form.dispatchEvent(new CustomEvent("input"));
      };
    }
  });
  form.output.remove();
  form.input.onchange();
  return form;
}
)})
    },
    {
      name: "textarea",
      inputs: ["input","html"],
      value: (function(input,html){return(
function textarea(config = {}) {
  let {value, title, description, autocomplete, cols = 45, rows = 3, width, height, maxlength, placeholder, spellcheck, wrap, submit} = config;
  if (typeof config == "string") value = config;
  if (value == null) value = "";
  const form = input({
    form: html`<form><textarea style="display: block; font-size: 0.8em;" name=input>${value}</textarea></form>`, 
    title, description, submit,
    attributes: {autocomplete, cols, rows, maxlength, placeholder, spellcheck, wrap}
  });
  form.output.remove();
  if (width != null) form.input.style.width = width;
  if (height != null) form.input.style.height = height;
  if (submit) form.submit.style.margin = "0";
  if (title || description) form.input.style.margin = "3px 0";
  return form;
}
)})
    },
    {
      name: "input",
      inputs: ["html","d3format"],
      value: (function(html,d3format){return(
function input(config) {
  let {
    form,
    type = "text",
    attributes = {},
    action,
    getValue,
    title,
    description,
    format,
    display,
    submit,
    options
  } = config;
  if (!form)
    form = html`<form>
	<input name=input type=${type} />
  </form>`;
  const input = form.input;
  Object.keys(attributes).forEach(key => {
    const val = attributes[key];
    if (val != null) input.setAttribute(key, val);
  });
  if (submit)
    form.append(
      html`<input name=submit type=submit style="margin: 0 0.75em" value="${
        typeof submit == "string" ? submit : "Submit"
      }" />`
    );
  form.append(
    html`<output name=output style="font: 14px Menlo, Consolas, monospace; margin-left: 0.5em;"></output>`
  );
  if (title)
    form.prepend(
      html`<div style="font: 700 0.9rem sans-serif;">${title}</div>`
    );
  if (description)
    form.append(
      html`<div style="font-size: 0.85rem; font-style: italic;">${description}</div>`
    );
  if (format) format = d3format.format(format);
  if (action) {
    action(form);
  } else {
    const verb = submit
      ? "onsubmit"
      : type == "button"
        ? "onclick"
        : type == "checkbox" || type == "radio"
          ? "onchange"
          : "oninput";
    form[verb] = e => {
      e && e.preventDefault();
      const value = getValue ? getValue(input) : input.value;
      if (form.output)
        form.output.value = display
          ? display(value)
          : format
            ? format(value)
            : value;
      form.value = value;
      if (verb !== "oninput")
        form.dispatchEvent(new CustomEvent("input", { bubbles: true }));
    };
    if (verb !== "oninput")
      input.oninput = e => e && e.stopPropagation() && e.preventDefault();
    if (verb !== "onsubmit") form.onsubmit = e => e && e.preventDefault();
    form[verb]();
  }
  return form;
}
)})
    },
    {
      name: "d3format",
      inputs: ["require"],
      value: (function(require){return(
require("d3-format@1")
)})
    }
  ]
};

const notebook = {
  id: "a9e838c1dd43780b@344",
  modules: [m0,m1]
};

export default notebook;
