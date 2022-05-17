
var gifSearch = angular.module('gifSearch', []);

gifSearch.controller('GifSearchController', function GifSearchController($scope, $http) {

    $scope.gifs = [];
    $scope.offset = 0;
    $scope.gif_name = ''

    $scope.changeGif = function () {

        
        if ($scope.gif_name != this.name) {
            $scope.gif_name = this.name;
            $scope.gifs = [];
            $scope.offset = 0;
        }

        console.log($scope.gif_name)
        var url = '/gif_search?q=' + $scope.gif_name + '&offset=0';

        $http({
            method: 'GET',
            url: url
        }).then(function successCallback(response) {

            $scope.gifs = response.data.data; //= response.data.data;
            console.log(response.data.data);
            
            // $('#gif-list').hide();

            $('#gif-list').on('DOMNodeInserted', '.ng-scope', function () {
                $('.gif-image').each(function(){ $(this).show(500); });
            });

            $('#show-more').show(500);

            // parent = document.getElementById('dest');
            var dest = document.getElementById("frame_dest");
            if (dest != null){
                $(dest).hide(500, function(){ $(dest).remove(); });
            }

            $scope.offset += 1

        }, function errorCallback(response) {
            
            $('#modal-title').text('Something Went Wrong :(')
            $("#modal-text").text("We were unable to get you some sweet reaction GIFs. Maybe try again later.")
            $('#myModal').modal('show');
            
        });
    }

    $scope.moreGif = function() {

        var url = '/gif_search?q=' + $scope.gif_name + '&offset=' + $scope.offset * 30;

        $http({
            method: 'GET',
            url: url
        }).then(function successCallback(response) {

            $scope.gifs.push(...response.data.data) //= response.data.data;
            console.log(response.data.data);
            
            // $('#gif-list').hide();

            $('#gif-list').on('DOMNodeInserted', '.ng-scope', function () {
                $('.gif-image').each(function(){ $(this).show(500); });
            });

            $scope.offset += 1;

        }, function errorCallback(response) {
            
            $('#modal-title').text('Something Went Wrong :(')
            $("#modal-text").text("We were unable to get you some sweet reaction GIFs. Maybe try again later.")
            $('#myModal').modal('show');
            
        });

    }
});