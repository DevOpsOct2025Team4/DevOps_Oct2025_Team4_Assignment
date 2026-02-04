var HttpHeader = Java.type("org.parosproxy.paros.network.HttpHeader");
var HttpRequestHeader = Java.type(
  "org.parosproxy.paros.network.HttpRequestHeader",
);
var URI = Java.type("org.apache.commons.httpclient.URI");
var ScriptVars = Java.type("org.zaproxy.zap.extension.script.ScriptVars");

function authenticate(helper, params, credentials) {
  var loginUrl = params.get("loginUrl");
  var usernameField = params.get("usernameField") || "email";
  var passwordField = params.get("passwordField") || "password";
  var username = credentials.getParam("username");
  var password = credentials.getParam("password");

  var msg = helper.prepareMessage();
  var uri = new URI(loginUrl, false);
  msg.setRequestHeader(
    new HttpRequestHeader(HttpRequestHeader.POST, uri, HttpHeader.HTTP11),
  );
  msg.getRequestHeader().setHeader(HttpHeader.CONTENT_TYPE, "application/json");
  msg.getRequestHeader().setHeader("Accept", "application/json");

  var payload = {};
  payload[usernameField] = username;
  payload[passwordField] = password;
  var body = JSON.stringify(payload);
  msg.setRequestBody(body);
  msg.getRequestHeader().setContentLength(body.length);

  helper.sendAndReceive(msg);

  try {
    var json = JSON.parse(msg.getResponseBody().toString());
    var token = json && json.session && json.session.access_token;
    if (token) {
      ScriptVars.setGlobalVar("auth.token", token);
    }
  } catch (e) {
    // ignore parsing errors
  }

  return msg;
}

function getRequiredParamsNames() {
  return ["loginUrl", "usernameField", "passwordField"];
}

function getOptionalParamsNames() {
  return [];
}

function getCredentialsParamsNames() {
  return ["username", "password"];
}
