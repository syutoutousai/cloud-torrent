/* globals app */

app.controller("DownloadsController", function($scope, $rootScope) {
  $rootScope.downloads = $scope;

  $scope.numDownloads = function() {
    if ($scope.state.Downloads && $scope.state.Downloads.Children)
      return $scope.state.Downloads.Children.length;
    return 0;
  };
});

app.controller("NodeController", function($scope, $rootScope, $http, $timeout) {
  var n = $scope.node;
  $scope.isfile = function() {
    return !n.Children;
  };
  $scope.isdir = function() {
    return !$scope.isfile();
  };

  var pathArray = [n.Name];
  if ($scope.$parent && $scope.$parent.$parent && $scope.$parent.$parent.node) {
    var parentNode = $scope.$parent.$parent.node;
    pathArray.unshift(parentNode.$path);
    n.$depth = parentNode.$depth + 1;
  } else {
    n.$depth = 1;
  }
  var path = (n.$path = pathArray.join("/"));
  n.$closed = $scope.agoHrs(n.Modified) > 24;

  $scope.isdownloading = function() {
    return false; // V1 fallback or default logic
  };

  $scope.preremove = function() {
    $scope.confirm = true;
    $timeout(function() {
      $scope.confirm = false;
    }, 3000);
  };

  //defaults
  $scope.closed = function() {
    return n.$closed;
  };
  $scope.toggle = function() {
    n.$closed = !n.$closed;
  };
  $scope.icon = function() {
    var c = [];
    c.push("outline");
    if ($scope.isfile()) {
      c.push("file");
    } else {
      c.push("folder");
      if (!$scope.closed()) c.push("open");
    }
    c.push("icon");
    return c.join(" ");
  };

  $scope.remove = function() {
    $http.delete("download/" + n.$path);
  };
});
