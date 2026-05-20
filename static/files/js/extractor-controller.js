/* globals app,window,angular */

app.controller("ExtractorController", function(
  $scope,
  $rootScope,
  storage,
  api,
  search
) {
  $rootScope.extractor = $scope;
  $scope.edit = false;
  $scope.activeTab = "query";
  $scope.inputs = {
    searchQuery: "",
    selectedProvider: storage.tcExtractorProvider || "",
    seedInput: ""
  };
  $scope.extractorFeedback = null;
  $scope.enrichFeedback = null;
  $scope.autoExtracting = false;
  $scope.providers = {};
  
  $scope.audit = {
    type: "Empty Input",
    isValid: false,
    statusText: "No seed input provided yet.",
    labelColor: "grey",
    trackersCount: 0,
    infohash: "-",
    qualityAdvice: "",
    name: ""
  };

  // Watch selected provider and save in storage
  $scope.$watch("inputs.selectedProvider", function(p) {
    if (p) storage.tcExtractorProvider = p;
  });

  // Load and filter active search providers
  $rootScope.$watch("state.SearchProviders", function(searchProviders) {
    if (!searchProviders) return;
    $scope.providers = {};
    for (var id in searchProviders) {
      if (/\/item$/.test(id)) continue;
      $scope.providers[id] = searchProviders[id];
    }
    // Set default selected provider if not set
    var keys = Object.keys($scope.providers);
    if (keys.length > 0 && !$scope.inputs.selectedProvider) {
      $scope.inputs.selectedProvider = keys[0];
    }
  });

  $scope.selectTab = function(tab) {
    $scope.activeTab = tab;
    $scope.clearFeedback();
  };

  $scope.clearFeedback = function() {
    $scope.extractorFeedback = null;
    $scope.enrichFeedback = null;
  };

  // Modern robust public trackers for enrichment
  var PUBLIC_TRACKERS = [
    "udp://tracker.coppersurfer.tk:6969/announce",
    "udp://tracker.openbittorrent.com:80/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://tracker.opentrackr.org:1337/announce"
  ];

  // Helper to parse magnet link parameters manually
  var parseMagnetParams = function(magnetStr) {
    var result = { infohash: "", name: "", trackers: [] };
    if (!magnetStr || !magnetStr.startsWith("magnet:?")) return result;
    
    var query = magnetStr.substring(8);
    var parts = query.split("&");
    
    parts.forEach(function(part) {
      var kv = part.split("=");
      if (kv.length !== 2) return;
      var k = decodeURIComponent(kv[0]);
      var v = decodeURIComponent(kv[1]);
      
      if (k === "xt" && v.startsWith("urn:btih:")) {
        result.infohash = v.substring(9);
      } else if (k === "dn") {
        result.name = v;
      } else if (k === "tr") {
        result.trackers.push(v);
      }
    });
    return result;
  };

  // Real-time Validity Check & Quality Auditing
  $scope.auditInput = function() {
    var val = ($scope.inputs.seedInput || "").trim();

    if (!val) {
      $scope.audit = {
        type: "Empty Input",
        isValid: false,
        statusText: "No seed input provided yet.",
        labelColor: "grey",
        trackersCount: 0,
        infohash: "-",
        qualityAdvice: "",
        name: ""
      };
      return;
    }

    // 1. Infohash Check (40-char hex string)
    if (/^[a-fA-F0-9]{40}$/.test(val)) {
      $scope.audit = {
        type: "Raw Info Hash",
        isValid: true,
        statusText: "Valid 40-character hex code.",
        labelColor: "orange",
        trackersCount: 0,
        infohash: val.toLowerCase(),
        qualityAdvice: "⚠️ Raw infohashes contain zero trackers. Loading will enrich it with 4 public trackers for optimized peer discovery.",
        name: ""
      };
      return;
    }

    // 2. Magnet URI Check
    if (/^magnet:\?xt=urn:btih:[a-zA-Z0-9]+/i.test(val)) {
      var parsed = parseMagnetParams(val);
      if (!parsed.infohash || parsed.infohash.length < 32) {
        $scope.audit = {
          type: "Magnet URI",
          isValid: false,
          statusText: "Malformed magnet link (invalid btih).",
          labelColor: "red",
          trackersCount: 0,
          infohash: "-",
          qualityAdvice: "",
          name: ""
        };
        return;
      }
      
      var trackerCount = parsed.trackers.length;
      var advice = "";
      if (trackerCount === 0) {
        advice = "⚠️ Quality warning: This magnet link lacks track announce servers. Enrichment is highly recommended to fetch peers.";
      } else if (trackerCount < 3) {
        advice = "💡 Quality tip: Few trackers are present. Enrichment will append 4 extra public trackers.";
      } else {
        advice = "✅ Quality check: Healthy magnet link containing " + trackerCount + " tracker announces.";
      }

      $scope.audit = {
        type: "Magnet URI",
        isValid: true,
        statusText: "Well-formed magnet link.",
        labelColor: "teal",
        trackersCount: trackerCount,
        infohash: parsed.infohash.toLowerCase(),
        qualityAdvice: advice,
        name: parsed.name
      };
      return;
    }

    // 3. HTTP Torrent URL Check
    if (/^https?:\/\//i.test(val)) {
      var isTorrentExtension = /\.torrent$/i.test(val);
      $scope.audit = {
        type: "HTTP Torrent URL",
        isValid: true,
        statusText: "Valid HTTP(S) network stream link.",
        labelColor: "blue",
        trackersCount: 0,
        infohash: "Loads dynamically on fetch",
        qualityAdvice: isTorrentExtension 
          ? "✅ Valid torrent link format. The server will download and load this .torrent file directly."
          : "💡 The URL will be loaded. Ensure the remote web server returns a valid .torrent binary.",
        name: ""
      };
      return;
    }

    // 4. Fallback Invalid Format
    $scope.audit = {
      type: "Invalid Format",
      isValid: false,
      statusText: "Input is not a valid 40-char infohash, magnet URI, or HTTP URL.",
      labelColor: "red",
      trackersCount: 0,
      infohash: "-",
      qualityAdvice: "",
      name: ""
    };
  };

  // Perform Seed Enrichment & Post to API
  $scope.enrichAndLoad = function() {
    if (!$scope.audit.isValid) return;

    var val = $scope.inputs.seedInput.trim();
    $scope.clearFeedback();

    var magnetURI = "";
    if ($scope.audit.type === "Raw Info Hash") {
      // Enrich infohash with trackers
      var hash = $scope.audit.infohash;
      magnetURI = "magnet:?xt=urn:btih:" + hash;
      PUBLIC_TRACKERS.forEach(function(tracker) {
        magnetURI += "&tr=" + encodeURIComponent(tracker);
      });
      
      $rootScope.apiing = true;
      api.magnet(magnetURI)
        .then(function(resp) {
          $scope.enrichFeedback = {
            ok: true,
            title: "Success",
            message: "Successfully enriched and registered raw Infohash as a magnet."
          };
          $scope.inputs.seedInput = "";
          $scope.auditInput();
        }, function(resp) {
          var err = resp.data || resp || {};
          $scope.enrichFeedback = {
            ok: false,
            title: "Error loading enriched infohash",
            message: err.error || err.message || err || "Request failed"
          };
        })
        .finally(function() {
          $rootScope.apiing = false;
        });

    } else if ($scope.audit.type === "Magnet URI") {
      var parsed = parseMagnetParams(val);
      // If magnet URI has no trackers, enrich it as well!
      if (parsed.trackers.length === 0) {
        magnetURI = val;
        PUBLIC_TRACKERS.forEach(function(tracker) {
          magnetURI += "&tr=" + encodeURIComponent(tracker);
        });
        val = magnetURI;
      }

      $rootScope.apiing = true;
      api.magnet(val)
        .then(function(resp) {
          $scope.enrichFeedback = {
            ok: true,
            title: "Success",
            message: "Successfully loaded magnet link."
          };
          $scope.inputs.seedInput = "";
          $scope.auditInput();
        }, function(resp) {
          var err = resp.data || resp || {};
          $scope.enrichFeedback = {
            ok: false,
            title: "Error loading magnet",
            message: err.error || err.message || err || "Request failed"
          };
        })
        .finally(function() {
          $rootScope.apiing = false;
        });

    } else if ($scope.audit.type === "HTTP Torrent URL") {
      $rootScope.apiing = true;
      api.url(val)
        .then(function(resp) {
          $scope.enrichFeedback = {
            ok: true,
            title: "Success",
            message: "Successfully loaded remote torrent file."
          };
          $scope.inputs.seedInput = "";
          $scope.auditInput();
        }, function(resp) {
          var err = resp.data || resp || {};
          $scope.enrichFeedback = {
            ok: false,
            title: "Error fetching torrent URL",
            message: err.error || err.message || err || "Request failed"
          };
        })
        .finally(function() {
          $rootScope.apiing = false;
        });
    }
  };

  // Perform Auto-Extraction Search & Download
  $scope.autoExtractBest = function() {
    if (!$scope.inputs.searchQuery) return;
    
    $scope.clearFeedback();
    $scope.autoExtracting = true;

    var provider = $scope.inputs.selectedProvider;
    var query = $scope.inputs.searchQuery;

    search.all(provider, query, 1)
      .then(function(resp) {
        var results = resp.data;
        if (!results || results.length === 0) {
          $scope.extractorFeedback = {
            ok: false,
            title: "Zero Results",
            message: "No results returned by provider '" + provider + "' for query: '" + query + "'"
          };
          $scope.autoExtracting = false;
          return;
        }

        // Parse seeds counts and sort descending
        var getSeedCount = function(item) {
          try {
            var s = parseInt(item.seeds || 0, 10);
            return isNaN(s) ? 0 : s;
          } catch(e) {
            return 0;
          }
        };

        var sorted = results.slice().sort(function(a, b) {
          return getSeedCount(b) - getSeedCount(a);
        });

        var best = sorted[0];
        
        // Quality check
        var seeds = getSeedCount(best);
        var size = best.size || "unknown size";
        var title = best.name || "Unknown Torrent";
        
        var completeLoad = function(seedTarget, isMagnet) {
          var action = isMagnet ? api.magnet(seedTarget) : api.url(seedTarget);
          
          action
            .then(function(resp) {
              $scope.extractorFeedback = {
                ok: true,
                title: "Successfully Extracted Best Seed",
                message: "Auto-selected and loaded '" + title + "' (" + size + ")",
                details: "Health Assessment: " + seeds + " seeds, " + (best.peers || "0") + " peers."
              };
              $scope.inputs.searchQuery = "";
            }, function(resp) {
              var err = resp.data || resp || {};
              $scope.extractorFeedback = {
                ok: false,
                title: "API Injection Failure",
                message: "Auto-selected candidate failed to load: " + (err.error || err.message || err || "Request failed")
              };
            })
            .finally(function() {
              $scope.autoExtracting = false;
            });
        };

        // Resolve magnet link or download URL
        if (best.magnet) {
          completeLoad(best.magnet, true);
        } else if (best.torrent) {
          // If relative path, enrich with provider origin
          var targetUrl = best.torrent;
          var providerInfo = $scope.state.SearchProviders[provider];
          if (/^\//.test(targetUrl) && providerInfo && providerInfo.url) {
            var origin = /(https?:\/\/[^\/]+)/.test(providerInfo.url) && RegExp.$1;
            if (origin) {
              targetUrl = origin + targetUrl;
            }
          }
          completeLoad(targetUrl, false);
        } else if (best.path) {
          // Single-item detail lookup is required
          search.one(provider, best.path)
            .then(function(resp) {
              var data = resp.data;
              if (data && data.magnet) {
                completeLoad(data.magnet, true);
              } else if (data && data.torrent) {
                var singleTarget = data.torrent;
                var singleProviderInfo = $scope.state.SearchProviders[provider];
                if (/^\//.test(singleTarget) && singleProviderInfo && singleProviderInfo.url) {
                  var singleOrigin = /(https?:\/\/[^\/]+)/.test(singleProviderInfo.url) && RegExp.$1;
                  if (singleOrigin) {
                    singleTarget = singleOrigin + singleTarget;
                  }
                }
                completeLoad(singleTarget, false);
              } else {
                $scope.extractorFeedback = {
                  ok: false,
                  title: "Extraction Error",
                  message: "Best candidate detail lookup did not contain a magnet or torrent file link."
                };
                $scope.autoExtracting = false;
              }
            }, function(err) {
              $scope.extractorFeedback = {
                ok: false,
                title: "Failed detail lookup",
                message: err.data ? (err.data.error || err.data) : "Network timeout"
              };
              $scope.autoExtracting = false;
            });
        } else {
          $scope.extractorFeedback = {
            ok: false,
            title: "Extraction Error",
            message: "Best candidate does not contain a valid magnet or download path."
          };
          $scope.autoExtracting = false;
        }
      }, function(resp) {
        var err = resp.data || resp || {};
        $scope.extractorFeedback = {
          ok: false,
          title: "Search Query Failed",
          message: err.error || err.message || err || "Request failed"
        };
        $scope.autoExtracting = false;
      });
  };
});
