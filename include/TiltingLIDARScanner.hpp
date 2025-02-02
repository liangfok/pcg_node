/*
 * Copyright (C) 2015 The University of Texas at Austin.
 * All rights reserved.
 *
 * This program is free software: you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation, either version 2.1 of
 * the License, or (at your option) any later version. See
 * <http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this program.  If not, see
 * <http://www.gnu.org/licenses/>
 */

#ifndef __TILTING_LIDAR_SCANNER_HPP__
#define __TILTING_LIDAR_SCANNER_HPP__

#include "ros/ros.h"

#include "sensor_msgs/LaserScan.h"
#include "sensor_msgs/PointCloud2.h"
#include "std_msgs/Int32.h"
#include "tilting_lidar_scanner/PointCloudSliceMsg.h"

#include <mutex>
#include <SerialStream.h>
#include <SerialStreamBuf.h>

#include "MCU.hpp"
#include "PointCloudAssembler.hpp"

namespace tiltingLIDARScanner {

/*!
 * The main ROS node for controlling the TiltingLIDARScanner.
 */
class TiltingLIDARScanner
{
public:
    /*!
     * The default constructor.
     */
    TiltingLIDARScanner();

    /*!
     * The destructor.
     */
    virtual ~TiltingLIDARScanner();

    /*!
     * Initializes the tilting LIDAR scanner.
     *
     * \return Whether the initialization was successful.
     */
    bool init();

    /*!
     * Starts the tilting LIDAR scanner.
     *
     * \return Whether the start was successful.
     */
    bool start();

    /*!
     * Stops the tilting LIDAR sensor. This should be called
     * before the program exits.
     */
    bool stop();

private:
    /*!
     * The callback function for the subscription to laser scan messages.
     * It stores the laser scan information in the laserScan member variable so that
     * it can be accessed in a real-time-safe manner.
     *
     * \param scan A message containing the laser scan data.
     */
    void laserScanCallback(const sensor_msgs::LaserScan & scan);

    /*!
     * The callback function for commands issued to this node.
     *
     * \param cmd The command.
     */
    void cmdCallback(const std_msgs::Int32 & cmd);

    /*!
     * Obtain a single slice of the point cloud.
     * This involves (1) telling the micro-controller to tilt
     * the stand by one step, (2) obtaining the current tilt angle
     * from the stand, (3) obtaining the current laser scan, and
     * (4) saving the laser scan into a point cloud.
     *
     * \return Whether a slice was successfully obtained.
     */
    bool obtainSlice();

    /*!
     * The ROS node handle.
     */
    ros::NodeHandle nh;

    /*!
     * The point cloud slice publisher and point cloud publisher.
     */
    ros::Publisher slicePublisher;

    /*!
     * The name of the ROS topic on which the laser scan is being published.
     */
    std::string laserScanTopic;

    /*!
     * The ROS topic subscriber for laser scan data.
     */
    ros::Subscriber laserScanSubscriber;

    /*!
     * The ROS topic subscriber for laser scan data.
     */
    ros::Subscriber cmdSubscriber;

    /*!
     * Stores the most recently received laser scan.
     */
    sensor_msgs::LaserScan laserScan;

    /*!
     * The message that's published by the slicePublisher.
     */
    tilting_lidar_scanner::PointCloudSliceMsg sliceMsg;

    /*!
     * The state of this node, either STATE_ENABLED or STATE_DISABLED.
     */
    int state;

    /*!
     * Mutexes for protecting variables that are shared between the ROS topic
     * subscriber callback thread and the main thread.
     */
    std::mutex scanMutex, stateMutex;

    /*!
     * Interface to the micro-controller.
     */
    MCU mcu;

    /*!
     * The object that actually constructs the point cloud from
     * slice information.
     */
    PointCloudAssembler pc;
};

} // namespace tiltingLIDARScanner

#endif // __TILTING_LIDAR_SCANNER_HPP__
