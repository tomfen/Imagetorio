import pako from "pako";

export function exportBlueprint(obj) {
  var string = JSON.stringify(obj);
  var binaryString = pako.deflate(string, { to: "string" });
  var base64 = btoa(binaryString);
  return "0" + base64;
}
