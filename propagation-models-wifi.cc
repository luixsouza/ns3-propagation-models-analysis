#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/internet-module.h"
#include "ns3/stats-module.h"
#include "ns3/applications-module.h"
#include <fstream>
#include <iostream>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("PropagationWifi");

double g_signalDbmAvg = 0;
uint32_t g_samples = 0;
uint64_t g_lastTotalRx = 0;
std::ofstream g_outCsv;

void MonitorSnifferRx (Ptr<const Packet> packet, uint16_t channelFreqMhz, WifiTxVector txVector, MpduInfo aMpdu, SignalNoiseDbm signalNoise, uint16_t staId)
{
    g_signalDbmAvg += signalNoise.signal;
    g_samples++;
}

void RecordData (Ptr<PacketSink> sink, Ptr<Node> nodeRx, Ptr<Node> nodeTx, double interval) {
    Ptr<MobilityModel> mobRx = nodeRx->GetObject<MobilityModel>();
    Ptr<MobilityModel> mobTx = nodeTx->GetObject<MobilityModel>();

    double dist = mobRx->GetDistanceFrom (mobTx);

    uint64_t totalRx = sink->GetTotalRx();
    double throughput = ((totalRx - g_lastTotalRx) * 8.0) / (interval * 1000000.0); // Mbps
    g_lastTotalRx = totalRx;

    double rss = (g_samples > 0) ? (g_signalDbmAvg / g_samples) : -100.0;
    g_signalDbmAvg = 0;
    g_samples = 0;

    if (g_outCsv.is_open()) {
        g_outCsv << dist << "," << rss << "," << throughput << std::endl;
    }

    Simulator::Schedule (Seconds(interval), &RecordData, sink, nodeRx, nodeTx, interval);
}

int main (int argc, char *argv[]) {
  uint32_t modelSelect = 0;
  double increment = 5.0; 
  double simTime = 100.0; 
  uint32_t seed = 1;

  CommandLine cmd;
  cmd.AddValue ("model", "Modelo", modelSelect);
  cmd.AddValue ("increment", "Velocidade", increment); 
  cmd.AddValue ("time", "Tempo", simTime);
  cmd.AddValue ("seed", "Seed", seed);
  cmd.Parse (argc, argv);

  RngSeedManager::SetSeed (seed);
  RngSeedManager::SetRun (1);

  NodeContainer nodes; nodes.Create (2);

  WifiHelper wifi;
  wifi.SetStandard (WIFI_STANDARD_80211n);
  YansWifiPhyHelper wifiPhy;
  YansWifiChannelHelper wifiChannel;
  wifiChannel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel");

  std::string modelName = "Friis";
  if(modelSelect==0) { wifiChannel.AddPropagationLoss ("ns3::FriisPropagationLossModel"); modelName="Friis"; }
  else if(modelSelect==1) { wifiChannel.AddPropagationLoss ("ns3::FixedRssLossModel", "Rss", DoubleValue(-65.0)); modelName="FixedRss"; }
  else if(modelSelect==2) { wifiChannel.AddPropagationLoss ("ns3::ThreeLogDistancePropagationLossModel"); modelName="ThreeLog"; }
  else if(modelSelect==3) { wifiChannel.AddPropagationLoss ("ns3::TwoRayGroundPropagationLossModel"); modelName="TwoRay"; }
  else if(modelSelect==4) { wifiChannel.AddPropagationLoss ("ns3::NakagamiPropagationLossModel"); modelName="Nakagami"; }

  wifiPhy.SetChannel (wifiChannel.Create ());
  WifiMacHelper wifiMac;
  wifiMac.SetType ("ns3::AdhocWifiMac");
  NetDeviceContainer devices = wifi.Install (wifiPhy, wifiMac, nodes);

  MobilityHelper mobility;
  Ptr<ListPositionAllocator> posAlloc = CreateObject<ListPositionAllocator>();
  posAlloc->Add(Vector(0.0, 0.0, 1.5)); 
  posAlloc->Add(Vector(10.0, 0.0, 1.5)); 
  mobility.SetPositionAllocator(posAlloc);
  
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (nodes.Get(0)); 
  
  mobility.SetMobilityModel ("ns3::ConstantVelocityMobilityModel");
  mobility.Install (nodes.Get(1)); 
  nodes.Get(1)->GetObject<ConstantVelocityMobilityModel>()->SetVelocity(Vector(increment, 0.0, 0.0));

  InternetStackHelper internet; internet.Install (nodes);
  Ipv4AddressHelper ipv4; ipv4.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer i = ipv4.Assign (devices);

  OnOffHelper onoff ("ns3::UdpSocketFactory", InetSocketAddress (i.GetAddress (1), 9));
  onoff.SetConstantRate (DataRate ("50Mbps"));
  onoff.SetAttribute ("PacketSize", UintegerValue (1024));
  
  ApplicationContainer apps = onoff.Install (nodes.Get (0));
  apps.Start (Seconds (0.5));
  apps.Stop (Seconds (simTime));

  PacketSinkHelper sink ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), 9));
  ApplicationContainer sinkApp = sink.Install (nodes.Get (1));
  sinkApp.Start (Seconds (0.0));
  sinkApp.Stop (Seconds (simTime));

  std::string filename = "ns_" + modelName + "_S" + std::to_string(seed) + ".csv";
  g_outCsv.open (filename);
  g_outCsv << "Distancia,RSS,Throughput" << std::endl;

  Config::ConnectWithoutContext ("/NodeList/1/DeviceList/0/$ns3::WifiNetDevice/Phy/MonitorSnifferRx", MakeCallback (&MonitorSnifferRx));

  Simulator::Schedule (Seconds (1.0), &RecordData, DynamicCast<PacketSink>(sinkApp.Get(0)), nodes.Get(1), nodes.Get(0), 0.5);
  Simulator::Stop (Seconds (simTime));
  Simulator::Run ();
  
  g_outCsv.close();
  Simulator::Destroy ();
  return 0;
}