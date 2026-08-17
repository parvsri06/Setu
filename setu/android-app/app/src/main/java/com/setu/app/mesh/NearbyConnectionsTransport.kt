package com.setu.app.mesh

/**
 * MeshTransport implementation backed by Android's Nearby Connections API
 * (P2P_CLUSTER strategy). This is the ONLY file that should import
 * com.google.android.gms.nearby.* — see MeshTransport.kt for why.
 *
 * Flow to implement (see ../../../../../docs/architecture.md):
 * discover -> connect -> exchange manifest -> diff -> transfer -> merge -> disconnect
 */
class NearbyConnectionsTransport : MeshTransport {

    override fun startDiscovery() {
        TODO("Not yet implemented")
    }

    override fun stopDiscovery() {
        TODO("Not yet implemented")
    }

    override fun onPeerConnected(callback: (peerId: String) -> Unit) {
        TODO("Not yet implemented")
    }

    override fun sendManifest(peerId: String, recordKeys: List<String>) {
        TODO("Not yet implemented")
    }

    override fun onManifestReceived(callback: (peerId: String, recordKeys: List<String>) -> Unit) {
        TODO("Not yet implemented")
    }

    override fun sendRecords(peerId: String, records: List<ByteArray>) {
        TODO("Not yet implemented")
    }

    override fun onRecordsReceived(callback: (peerId: String, records: List<ByteArray>) -> Unit) {
        TODO("Not yet implemented")
    }
}
