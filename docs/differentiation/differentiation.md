# Win With Vane

<div style='text-align: justify;'>
    In the traditional network operating model, network certification testing has been a barrier to network changes.  
</div>
<div style='text-align: justify;'>
    The problem is testing can take a significant amount of time which is usually measured in months.  During this time organizations are prevented from taking advantage of new platform economics like transitioning to higher speed ethernet which can reduce the number of links required in a topology, or using new silicon which creates higher port density and improves scaling.  It also prevents new features from entering the network which could simplify functionality or be applied to a service.  Lastly, it prevents a new service that could create new revenue streams for the organization from being introduced.
</div>
<div style='text-align: justify;'>
    Using the Vane Testing Framework and Arista’s expertise, network certification test cases can be automated.  This is disruptive to traditional network certification testing because it is easy to use, easy to create test cases, and fast.
</div>
Below are the benefits of Vane Testing Framework:

## **Versatility in Testing Scenarios**

*Traditional and Advanced Tests:* While NRFU testing focuses on basic readiness,
our framework extends its capabilities to conduct a wide range of tests,
including performance, security, scalability, and hardware tests.
This ensures that the network is not only ready but optimized for diverse scenarios.

## **Real-world Network Testing**

*Physical and Virtual Environments:* Our framework breaks the barrier between
virtual and physical networks. It not only lets you test your virtual network
twin but also allows for testing on actual hardware, ensuring that the
network's real-world performance matches expectations. This is crucial for
industries where physical infrastructure plays a significant role.

## **Holistic Network-wide Validation**

*Beyond Single Device Testing:* Our framework takes a holistic approach by
communicating with and testing the entire network, not just individual devices.
This ensures that the network as a whole is thoroughly validated, identifying
potential bottlenecks, inter-device dependencies, and overall system efficiency.

## **Ease of Integration with Existing Workflows**

*Customization and Adaptability:* By supporting configurations ingested
from AVD or YAML files, Vane aligns with existing development and operational
workflows. This ensures a smooth integration process for organizations that have
established practices using specific tools or file formats. The tool becomes an
integral part of the existing ecosystem, minimizing disruptions and accelerating the
adoption of network validation practices.

## **Open Source**

The Vane Testing Framework is open source and available on Arista Network’s public [GitHub repository](https://github.com/aristanetworks/vane). The repository includes the Vane application and sample test cases.  

Open source software is free to use, reducing costs for organizations to adapt.  Users have the freedom to modify and adapt the software to meet their specific needs.  With many eyes on the code, vulnerabilities can be identified and fixed quickly, enhancing the software's security.  Open source projects have strong communities that offer support, contribute to development, and share knowledge.  Open source fosters innovation as developers from around the world can contribute new ideas and improvements.

## **Agnostic to Infrastructure**

The Vane application is designed to run on any platform including local computing like a laptop or a desktop, a server, or the cloud.  Vane can run on any Unix or Windows platform, in a Python virtual environment, or within a container.  There is also a CloudVision application available.

The Vane application is able to qualify physical network infrastructure, virtual network infrastructure like Arista Cloud Test, or a hybrid of virtual and physical.  Using virtual infrastructure can greatly reduce the cost of testing and increase test coverage.  However, some tests will require physical hardware if the virtual infrastructure cannot be replicated in software like Quality of Service or Multicast forwarding tests.  It should be noted Vane is unable to replace tests which require human interaction like removing components within an Arista switch.
