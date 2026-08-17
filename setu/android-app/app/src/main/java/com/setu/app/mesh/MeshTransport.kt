package com.setu.app.mesh

/**
 * Transport-agnostic interface for the mesh layer.
 *
 * IMPORTANT: nothing outside this package should talk to Nearby Connections
 * directly. Sync logic and UI talk to THIS interface only. That's what
 * lets a custom cross-platform BLE protocol replace the implementation
 * later without touching anything built on top of it.
 */
interface MeshTransport {
    fun startDiscovery()
    fun stopDiscovery()
    fun onPeerConnected(callback: (peerId: String) -> Unit)
    fun sendManifest(peerId: String, recordKeys: List<String>)
    fun onManifestReceived(callback: (peerId: String, recordKeys: List<String>) -> Unit)
    fun sendRecords(peerId: String, records: List<ByteArray>)
    fun onRecordsReceived(callback: (peerId: String, records: List<ByteArray>) -> Unit)
}
