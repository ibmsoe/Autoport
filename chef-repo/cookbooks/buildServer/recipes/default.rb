#
# Cookbook Name:: buildServer
# Recipe:: default
#
# Copyright 2015, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

include_recipe 'repo_settings'
include_recipe 'buildServer::buildtools'
include_recipe 'buildServer::managedPackages'
include_recipe 'buildServer::java'
include_recipe 'buildServer::ant'
include_recipe 'buildServer::maven'
include_recipe 'buildServer::protobuf_source'
include_recipe 'buildServer::scala'
include_recipe 'buildServer::gradle'
include_recipe 'buildServer::nodejs'
