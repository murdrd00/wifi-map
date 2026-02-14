import CoreWLAN
import Foundation

// Swift helper to scan WiFi networks using CoreWLAN.
// Outputs JSON with connected network info + all visible networks.
// Usage: swift wifi_scan.swift

var output: [String: Any] = [:]

guard let iface = CWWiFiClient.shared().interface() else {
    output["error"] = "No WiFi interface found"
    if let data = try? JSONSerialization.data(withJSONObject: output),
       let str = String(data: data, encoding: .utf8) {
        print(str)
    }
    exit(1)
}

// Connected network info
output["rssi"] = iface.rssiValue()
output["noise"] = iface.noiseMeasurement()
output["channel"] = iface.wlanChannel()?.channelNumber ?? 0
output["tx_rate"] = iface.transmitRate()
output["ssid"] = iface.ssid() ?? nil  // nil if Location Services not granted

func bandString(_ ch: CWChannel?) -> String {
    switch ch?.channelBand {
    case .band2GHz: return "2.4 GHz"
    case .band5GHz: return "5 GHz"
    case .band6GHz: return "6 GHz"
    default: return "unknown"
    }
}

output["band"] = bandString(iface.wlanChannel())

// Scan for all nearby networks
var networks: [[String: Any]] = []
if let scanResults = try? iface.scanForNetworks(withName: nil) {
    for n in scanResults {
        var net: [String: Any] = [:]
        net["ssid"] = n.ssid ?? ""
        net["bssid"] = n.bssid ?? ""
        net["rssi"] = n.rssiValue
        net["noise"] = n.noiseMeasurement
        net["channel"] = n.wlanChannel?.channelNumber ?? 0
        net["band"] = bandString(n.wlanChannel)

        // Try to identify the connected network by matching channel + similar RSSI
        let connectedChannel = iface.wlanChannel()?.channelNumber ?? -1
        let connectedRssi = iface.rssiValue()
        if n.wlanChannel?.channelNumber == connectedChannel &&
           abs(n.rssiValue - connectedRssi) <= 5 &&
           output["ssid"] as? String == nil {
            output["ssid"] = n.ssid
            net["is_connected"] = true
        }

        networks.append(net)
    }
}

// Sort by signal strength (strongest first)
networks.sort { ($0["rssi"] as? Int ?? -100) > ($1["rssi"] as? Int ?? -100) }
output["networks"] = networks

if let data = try? JSONSerialization.data(withJSONObject: output),
   let str = String(data: data, encoding: .utf8) {
    print(str)
}
