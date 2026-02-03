var ScriptVars = Java.type("org.zaproxy.zap.extension.script.ScriptVars");

function sendingRequest(msg, initiator, helper) {
  var token = ScriptVars.getGlobalVar("auth.token");
  if (!token) {
    return;
  }
  var url = msg.getRequestHeader().getURI().toString();
  if (url.indexOf("/api/login") !== -1) {
    return;
  }
  msg.getRequestHeader().setHeader("Authorization", "Bearer " + token);
}

function responseReceived(msg, initiator, helper) {}
