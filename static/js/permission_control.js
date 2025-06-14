// permission_control.js
const API_BASE_URL = "http://127.0.0.1:8000";  // 替换为生产地址

let currentUserRole = null;
let currentUserPermissions = {};

// 页面加载时获取用户权限
$(document).ready(() => {
  fetchUserPermissions();
});

function fetchUserPermissions() {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    console.warn("未登录，无法加载权限");
    return;
  }
  $.get(`${API_BASE_URL}/api/permissions/user/${userId}`, data => {
    currentUserRole = data.role;
    currentUserPermissions = data.permissions;  // {"module_name": true/false}
    applyPermissionUI();
  }).fail(() => {
    console.error("获取权限失败");
  });
}

function applyPermissionUI() {
  // 控制权限管理按钮
  if (!currentUserPermissions['permission_management']) {
    $("#permission-btn").hide();
  } else {
    $("#permission-btn").show();
  }

  // 控制票务后台按钮
  if (!currentUserPermissions['ticket_management']) {
    $(".ticket-admin").hide();
  } else {
    $(".ticket-admin").show();
  }

  // 示例：控制统计功能
  if (!currentUserPermissions['stats_view']) {
    $(".stats-section").hide();
  }
}
